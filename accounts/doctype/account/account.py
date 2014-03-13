# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import webnotes

from webnotes.utils import flt, fmt_money, cstr, cint
from webnotes import msgprint, _

get_value = webnotes.conn.get_value

class DocType:
	def __init__(self,d,dl):
		self.doc, self.doclist = d,dl
		self.nsm_parent_field = 'parent_account'

	def autoname(self):
		self.doc.name = self.doc.account_name.strip() + ' - ' + \
			webnotes.conn.get_value("Company", self.doc.company, "abbr")

	def get_address(self):
		return {
			'address': webnotes.conn.get_value(self.doc.master_type, 
				self.doc.master_name, "address")
		}
		
	def validate(self): 
		self.validate_master_name()
		self.validate_parent()
		self.validate_duplicate_account()
		self.validate_root_details()
		self.validate_mandatory()
		self.validate_warehouse_account()
		self.validate_frozen_accounts_modifier()
	
		if not self.doc.parent_account:
			self.doc.parent_account = ''
		
	def validate_master_name(self):
		"""Remind to add master name"""
		# webnotes.errprint([self.doc.company,self.doc.master_type, self.doc.account_type])
		if self.doc.master_type in ('Customer', 'Supplier') or self.doc.account_type == "Warehouse":
			if not self.doc.master_name:
				msgprint(_("Please enter Master Name once the account is created."))
			elif not webnotes.conn.exists(self.doc.master_type or self.doc.account_type, 
					self.doc.master_name):
				webnotes.throw(_("Invalid Master Name"))
			
	def validate_parent(self):
		"""Fetch Parent Details and validation for account not to be created under ledger"""
		if self.doc.parent_account:
			par = webnotes.conn.sql("""select name, group_or_ledger, is_pl_account, debit_or_credit 
				from tabAccount where name =%s""", self.doc.parent_account)
			if not par:
				msgprint("Parent account does not exists", raise_exception=1)
			elif par[0][0] == self.doc.name:
				msgprint("You can not assign itself as parent account", raise_exception=1)
			elif par[0][1] != 'Group':
				msgprint("Parent account can not be a ledger", raise_exception=1)
			elif self.doc.debit_or_credit and par[0][3] != self.doc.debit_or_credit:
				msgprint("You can not move a %s account under %s account" % 
					(self.doc.debit_or_credit, par[0][3]), raise_exception=1)
			
			if not self.doc.is_pl_account:
				self.doc.is_pl_account = par[0][2]
			if not self.doc.debit_or_credit:
				self.doc.debit_or_credit = par[0][3]

	def validate_max_root_accounts(self):
		"""Raise exception if there are more than 4 root accounts"""
		if webnotes.conn.sql("""select count(*) from tabAccount where
			company=%s and ifnull(parent_account,'')='' and docstatus != 2""",
			self.doc.company)[0][0] > 4:
			webnotes.msgprint("One company cannot have more than 4 root Accounts",
				raise_exception=1)
	
	def validate_duplicate_account(self):
		if self.doc.fields.get('__islocal') or not self.doc.name:
			company_abbr = webnotes.conn.get_value("Company", self.doc.company, "abbr")
			if webnotes.conn.sql("""select name from tabAccount where name=%s""", 
				(self.doc.account_name + " - " + company_abbr)):
					msgprint("Account Name: %s already exists, please rename" 
						% self.doc.account_name, raise_exception=1)
				
	def validate_root_details(self):
		#does not exists parent
		if webnotes.conn.exists("Account", self.doc.name):
			if not webnotes.conn.get_value("Account", self.doc.name, "parent_account"):
				webnotes.msgprint("Root cannot be edited.", raise_exception=1)
				
	def validate_frozen_accounts_modifier(self):
		old_value = webnotes.conn.get_value("Account", self.doc.name, "freeze_account")
		if old_value and old_value != self.doc.freeze_account:
			frozen_accounts_modifier = webnotes.conn.get_value( 'Accounts Settings', None, 
				'frozen_accounts_modifier')
			if not frozen_accounts_modifier or \
				frozen_accounts_modifier not in webnotes.user.get_roles():
					webnotes.throw(_("You are not authorized to set Frozen value"))
			
	def convert_group_to_ledger(self):
		if self.check_if_child_exists():
			msgprint("Account: %s has existing child. You can not convert this account to ledger" % 
				(self.doc.name), raise_exception=1)
		elif self.check_gle_exists():
			msgprint("Account with existing transaction can not be converted to ledger.", 
				raise_exception=1)
		else:
			self.doc.group_or_ledger = 'Ledger'
			self.doc.save()
			return 1

	def convert_ledger_to_group(self):
		if self.check_gle_exists():
			msgprint("Account with existing transaction can not be converted to group.", 
				raise_exception=1)
		elif self.doc.master_type or self.doc.account_type:
			msgprint("Cannot covert to Group because Master Type or Account Type is selected.", 
				raise_exception=1)
		else:
			self.doc.group_or_ledger = 'Group'
			self.doc.save()
			return 1

	# Check if any previous balance exists
	def check_gle_exists(self):
		return webnotes.conn.get_value("GL Entry", {"account": self.doc.name})

	def check_if_child_exists(self):
		return webnotes.conn.sql("""select name from `tabAccount` where parent_account = %s 
			and docstatus != 2""", self.doc.name)
	
	def validate_mandatory(self):
		if not self.doc.debit_or_credit:
			msgprint("Debit or Credit field is mandatory", raise_exception=1)
		if not self.doc.is_pl_account:
			msgprint("Is PL Account field is mandatory", raise_exception=1)
			
	def validate_warehouse_account(self):
		if not cint(webnotes.defaults.get_global_default("auto_accounting_for_stock")):
			return
			
		if self.doc.account_type == "Warehouse":
			old_warehouse = cstr(webnotes.conn.get_value("Account", self.doc.name, "master_name"))
			if old_warehouse != cstr(self.doc.master_name):
				if old_warehouse:
					self.validate_warehouse(old_warehouse)
				if self.doc.master_name:
					self.validate_warehouse(self.doc.master_name)
				else:
					webnotes.throw(_("Master Name is mandatory if account type is Warehouse"))
		
	def validate_warehouse(self, warehouse):
		if webnotes.conn.get_value("Stock Ledger Entry", {"warehouse": warehouse}):
			webnotes.throw(_("Stock transactions exist against warehouse ") + warehouse + 
				_(" .You can not assign / modify / remove Master Name"))

	def update_nsm_model(self):
		"""update lft, rgt indices for nested set model"""
		import webnotes
		import webnotes.utils.nestedset
		webnotes.utils.nestedset.update_nsm(self)
			
	def on_update(self):
		self.validate_max_root_accounts()
		self.update_nsm_model()		

	def get_authorized_user(self):
		# Check logged-in user is authorized
		if webnotes.conn.get_value('Accounts Settings', None, 'credit_controller') \
				in webnotes.user.get_roles():
			return 1
			
	def check_credit_limit(self, total_outstanding):
		# Get credit limit
		credit_limit_from = 'Customer'

		cr_limit = webnotes.conn.sql("""select t1.credit_limit from tabCustomer t1, `tabAccount` t2 
			where t2.name=%s and t1.name = t2.master_name""", self.doc.name)
		credit_limit = cr_limit and flt(cr_limit[0][0]) or 0
		if not credit_limit:
			credit_limit = webnotes.conn.get_value('Company', self.doc.company, 'credit_limit')
			credit_limit_from = 'Company'
		
		# If outstanding greater than credit limit and not authorized person raise exception
		if credit_limit > 0 and flt(total_outstanding) > credit_limit \
				and not self.get_authorized_user():
			msgprint("""Total Outstanding amount (%s) for <b>%s</b> can not be \
				greater than credit limit (%s). To change your credit limit settings, \
				please update in the <b>%s</b> master""" % (fmt_money(total_outstanding), 
				self.doc.name, fmt_money(credit_limit), credit_limit_from), raise_exception=1)
			
	def validate_trash(self):
		"""checks gl entries and if child exists"""
		if not self.doc.parent_account:
			msgprint("Root account can not be deleted", raise_exception=1)
			
		if self.check_gle_exists():
			msgprint("""Account with existing transaction (Sales Invoice / Purchase Invoice / \
				Journal Voucher) can not be deleted""", raise_exception=1)
		if self.check_if_child_exists():
			msgprint("Child account exists for this account. You can not delete this account.",
			 	raise_exception=1)

	def on_trash(self): 
		self.validate_trash()
		self.update_nsm_model()
		
	def before_rename(self, old, new, merge=False):
		# Add company abbr if not provided
		from setup.doctype.company.company import get_name_with_abbr
		new_account = get_name_with_abbr(new, self.doc.company)
		
		# Validate properties before merging
		if merge:
			if not webnotes.conn.exists("Account", new):
				webnotes.throw(_("Account ") + new +_(" does not exists"))
				
			val = list(webnotes.conn.get_value("Account", new_account, 
				["group_or_ledger", "debit_or_credit", "is_pl_account"]))
			
			if val != [self.doc.group_or_ledger, self.doc.debit_or_credit, self.doc.is_pl_account]:
				webnotes.throw(_("""Merging is only possible if following \
					properties are same in both records.
					Group or Ledger, Debit or Credit, Is PL Account"""))
					
		return new_account

	def after_rename(self, old, new, merge=False):
		if not merge:
			webnotes.conn.set_value("Account", new, "account_name", 
				" - ".join(new.split(" - ")[:-1]))
		else:
			from webnotes.utils.nestedset import rebuild_tree
			rebuild_tree("Account", "parent_account")

def get_master_name(doctype, txt, searchfield, start, page_len, filters):
	conditions = (" and company='%s'"% filters["company"]) if doctype == "Warehouse" else ""
		
	return webnotes.conn.sql("""select name from `tab%s` where %s like %s %s
		order by name limit %s, %s""" %
		(filters["master_type"], searchfield, "%s", conditions, "%s", "%s"), 
		("%%%s%%" % txt, start, page_len), as_list=1)
		
def get_parent_account(doctype, txt, searchfield, start, page_len, filters):
	return webnotes.conn.sql("""select name from tabAccount 
		where group_or_ledger = 'Group' and docstatus != 2 and company = %s
		and %s like %s order by name limit %s, %s""" % 
		("%s", searchfield, "%s", "%s", "%s"), 
		(filters["company"], "%%%s%%" % txt, start, page_len), as_list=1)
