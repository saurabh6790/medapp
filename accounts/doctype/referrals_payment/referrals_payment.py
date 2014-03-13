# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes
from webnotes.model.doc import Document
from webnotes.model.doc import addchild
from webnotes.utils import flt,nowdate
sql = webnotes.conn.sql

class DocType:
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl
	
	def on_update(self):pass
		# webnotes.errprint('hell')
	
	def get_patient(self):
		patients = webnotes.conn.sql("""select parent from tabEncounter 
				where ifnull(is_payment_done,'False') = 'False' and referrer_name = '%s'"""%self.doc.doctor,as_dict=1)

		self.doclist = self.doc.clear_table(self.doclist, 'payment_details')
		
		comm_rule = webnotes.conn.sql("""select rules,value from tabLead where name ='%s'"""%self.doc.doctor,as_list=1)

		total_amount = 0
		inv = []
                for patient in patients:
			amount = webnotes.conn.sql("""select sum(grand_total_export), group_concat(concat("'",name,"'")) from `tabSales Invoice` 
				where ifnull(referrals_payment_done,'False')='False' and customer = '%s'"""%patient['parent'],as_list=1)
			# webnotes.errprint(amount)	
			cld = addchild(self.doc, 'payment_details', 'Referrals Payment Details',self.doclist)
                        cld.patient = patient['parent']

			if comm_rule:
				cld.commission_rules = comm_rule[0][0]
				if comm_rule[0][0] == 'Fixed Cost':
					cld.amount = comm_rule[0][1]
					cld.final_amount = comm_rule[0][1]
					total_amount += flt(comm_rule[0][1])
				else:
					cld.amount =  0.0
					cld.percent =  0.0
					cld.final_amount = 0.0
					if amount[0][0]: 
						cld.amount = amount[0][0] or 0.0
						cld.percent = comm_rule[0][1] or 0.0
						amt = flt(amount[0][0]) * flt(comm_rule[0][1])/(100)
						cld.final_amount = amt
						total_amount += flt(amt)
						inv.append(amount[0][1])

		self.doc.total_amount = total_amount
		self.doc.invoice = ','.join(inv)

	def make_bank_voucher(self):
		self.set_flag()
		"""
			get default bank account,default salary acount from company
		"""
		#amt = self.get_total_salary()
		com = webnotes.conn.sql("""select default_bank_account, default_expense_account from `tabCompany` 
			where name = '%s'""" % self.doc.company,as_list=1)		

		if not com[0][0] or not com[0][1]:
			msgprint("You can set Default Bank Account in Company master.")
		if not self.doc.jv:
			jv = Document('Journal Voucher')
			jv.voucher_type = 'Bank Voucher'
			jv.user_remark = 'Referrals Payment'
			jv.fiscal_year = '2013-14'
			jv.total_credit = jv.total_debit = self.doc.total_amount
			jv.company = self.doc.company
			jv.posting_date = nowdate()
			jv.save()
		
			jvd = Document('Journal Voucher Detail')
			jvd.account = com and com[0][0] or ''
			jvd.credit =  self.doc.total_amount
			jvd.parent = jv.name
			jvd.save()

			jvd1 = Document('Journal Voucher Detail')
			jvd1.account = com and com[0][1] or ''
			jvd1.debit = self.doc.total_amount
			jvd1.parent = jv.name
			jvd1.save()
		
			self.doc.jv = jv.name	
			self.doc.save()

	def set_flag(self):
		from webnotes.model.bean import getlist
		for g in getlist(self.doclist,'payment_details'):
			webnotes.conn.sql("update tabEncounter set is_payment_done = 'True' where parent = '%s'"%g.patient)
		webnotes.conn.sql("update `tabSales Invoice` set referrals_payment_done = 'True' where name in ("+self.doc.invoice+")")
			
