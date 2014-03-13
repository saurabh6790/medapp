# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import webnotes

from webnotes.model.doc import Document, make_autoname
from webnotes import msgprint, _
import webnotes.defaults


from utilities.transaction_base import TransactionBase

class DocType(TransactionBase):
	def __init__(self, doc, doclist=[]):
		self.doc = doc
		self.doclist = doclist
				
	def autoname(self):
		cust_master_name = webnotes.defaults.get_global_default('cust_master_name')
		# webnotes.errprint([cust_master_name,self.doc.doctype])
		if cust_master_name == 'Customer Name':
			if webnotes.conn.exists("Supplier", self.doc.customer_name):
				msgprint(_("A Supplier exists with same name"), raise_exception=1)
			self.doc.name = self.doc.customer_name
		else:
			self.doc.name = make_autoname(self.doc.naming_series+'.#####')

	def get_company_abbr(self):
		return webnotes.conn.get_value('Company', self.doc.company, 'abbr')

	def get_receivables_group(self):
		g = webnotes.conn.sql("select receivables_group from tabCompany where name=%s", self.doc.company)
		g = g and g[0][0] or '' 
		if not g:
			msgprint("Update Company master, assign a default group for Receivables")
			raise Exception
		return g
	
	def validate_values(self):
		if webnotes.defaults.get_global_default('cust_master_name') == 'Naming Series' and not self.doc.naming_series:
			webnotes.throw("Series is Mandatory.", webnotes.MandatoryError)

	def validate(self):
		self.validate_values()

	def update_lead_status(self):
		if self.doc.lead_name:
			webnotes.conn.sql("update `tabLead` set status='Converted' where name = %s", self.doc.lead_name)

	def update_address(self):
		webnotes.conn.sql("""update `tabAddress` set customer_name=%s, modified=NOW() 
			where customer=%s""", (self.doc.customer_name, self.doc.name))

	def update_contact(self):
		webnotes.conn.sql("""update `tabContact` set customer_name=%s, modified=NOW() 
			where customer=%s""", (self.doc.customer_name, self.doc.name))

	def create_account_head(self):
		# webnotes.errprint([self.doc.company,self.doc.master_type, self.doc.account_type])
		if self.doc.company :
			abbr = self.get_company_abbr()
			if not webnotes.conn.exists("Account", (self.doc.name + " - " + abbr)):
				parent_account = self.get_receivables_group()
				# create
				ac_bean = webnotes.bean({
					"doctype": "Account",
					'account_name': self.doc.name,
					'parent_account': parent_account, 
					'group_or_ledger':'Ledger',
					'company':self.doc.company, 
					'master_type':self.doc.master_type, 
					'master_name':self.doc.name,
					"freeze_account": "No"
				})
				ac_bean.ignore_permissions = True
				ac_bean.insert()
				
				msgprint(_("Account Head") + ": " + ac_bean.doc.name + _(" created"))
		else :
			msgprint(_("Please Select Company under which you want to create account head"))

	def update_credit_days_limit(self):
		webnotes.conn.sql("""update tabAccount set credit_days = %s, credit_limit = %s 
			where master_type='Customer' and master_name = %s""", 
			(self.doc.credit_days or 0, self.doc.credit_limit or 0, self.doc.name))

	def create_lead_address_contact(self):
		if self.doc.lead_name:
			if not webnotes.conn.get_value("Address", {"lead": self.doc.lead_name, "customer": self.doc.customer}):
				webnotes.conn.sql("""update `tabAddress` set customer=%s, customer_name=%s where lead=%s""", 
					(self.doc.name, self.doc.customer_name, self.doc.lead_name))

			lead = webnotes.conn.get_value("Lead", self.doc.lead_name, ["lead_name", "email_id", "phone", "mobile_no"], as_dict=True)
			c = Document('Contact') 
			c.first_name = lead.lead_name 
			c.email_id = lead.email_id
			c.phone = lead.phone
			c.mobile_no = lead.mobile_no
			c.customer = self.doc.name
			c.customer_name = self.doc.customer_name
			c.is_primary_contact = 1
			try:
				c.save(1)
			except NameError, e:
				pass

	def on_update(self):
		# webnotes.errprint([self.doc.company,self.doc.master_type, self.doc.account_type])
		self.validate_name_with_customer_group()
		
		self.update_lead_status()
		self.update_address()
		self.update_contact()

		# create account head
		self.create_account_head()
		# update credit days and limit in account
		self.update_credit_days_limit()
		#create address and contact from lead
		self.create_lead_address_contact()
		
	def validate_name_with_customer_group(self):
		if webnotes.conn.exists("Customer Group", self.doc.name):
			webnotes.msgprint("An Customer Group exists with same name (%s), \
				please change the Customer name or rename the Customer Group" % 
				self.doc.name, raise_exception=1)

	def delete_customer_address(self):
		addresses = webnotes.conn.sql("""select name, lead from `tabAddress`
			where customer=%s""", (self.doc.name,))
		
		for name, lead in addresses:
			if lead:
				webnotes.conn.sql("""update `tabAddress` set customer=null, customer_name=null
					where name=%s""", name)
			else:
				webnotes.conn.sql("""delete from `tabAddress` where name=%s""", name)
	
	def delete_customer_contact(self):
		for contact in webnotes.conn.sql_list("""select name from `tabContact` 
			where customer=%s""", self.doc.name):
				webnotes.delete_doc("Contact", contact)
	
	def delete_customer_account(self):
		"""delete customer's ledger if exist and check balance before deletion"""
		acc = webnotes.conn.sql("select name from `tabAccount` where master_type = 'Customer' \
			and master_name = %s and docstatus < 2", self.doc.name)
		if acc:
			from webnotes.model import delete_doc
			delete_doc('Account', acc[0][0])

	def on_trash(self):
		self.delete_customer_address()
		self.delete_customer_contact()
		self.delete_customer_account()
		if self.doc.lead_name:
			webnotes.conn.sql("update `tabLead` set status='Interested' where name=%s",self.doc.lead_name)
			
	def before_rename(self, olddn, newdn, merge=False):
		from accounts.utils import rename_account_for
		rename_account_for("Customer", olddn, newdn, merge)

	def after_rename(self, olddn, newdn, merge=False):
		set_field = ''
		if webnotes.defaults.get_global_default('cust_master_name') == 'Customer Name':
			webnotes.conn.set(self.doc, "customer_name", newdn)
			self.update_contact()
			set_field = ", customer_name=%(newdn)s"
		self.update_customer_address(newdn, set_field)

	def update_customer_address(self, newdn, set_field):
		webnotes.conn.sql("""update `tabAddress` set address_title=%(newdn)s 
			{set_field} where customer=%(newdn)s"""\
			.format(set_field=set_field), ({"newdn": newdn}))

@webnotes.whitelist()
def get_dashboard_info(customer):
	if not webnotes.has_permission("Customer", "read", customer):
		webnotes.msgprint("No Permission", raise_exception=True)
	
	out = {}
	for doctype in ["Opportunity", "Quotation", "Sales Order", "Delivery Note", "Sales Invoice"]:
		out[doctype] = webnotes.conn.get_value(doctype, 
			{"customer": customer, "docstatus": ["!=", 2] }, "count(*)")
	
	billing = webnotes.conn.sql("""select sum(grand_total), sum(outstanding_amount) 
		from `tabSales Invoice` 
		where customer=%s 
			and docstatus = 1
			and fiscal_year = %s""", (customer, webnotes.conn.get_default("fiscal_year")))
	
	out["total_billing"] = billing[0][0]
	out["total_unpaid"] = billing[0][1]
	
	return out
