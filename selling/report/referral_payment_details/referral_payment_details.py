# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd.
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import webnotes
from webnotes import _, msgprint

def execute(filters=None):
	if not filters: filters = {}
	
	columns = get_columns()
	data = get_entries(filters)
	
	return columns, data
	
def get_columns():
	return ['Account::80',"Referrer Id::120","Referral Name::120","Amount:Currency:120","Bill Number::120"]

def get_conditions(filters):
	conditions = ""
	if filters.get('from_date') and filters.get('to_date'):
		conditions += "and jv.posting_date between '%(from_date)s' and '%(to_date)s'"%filters 	
	
	return conditions
	
def get_entries(filters):
	conditions = get_conditions(filters)

	return webnotes.conn.sql("""SELECT distinct acc.name, acc.master_name, ld.lead_name, gl.credit, jv.against_bill FROM `tabGL Entry` gl,
		tabAccount acc, `tabJournal Voucher` jv, `tabSales Invoice` si, `tabSales Invoice Item` sii, tabLead ld 
		WHERE gl.against = acc.name
			AND acc.parent_account LIKE '%s'
			AND acc.master_type ='Lead'
			AND acc.group_or_ledger='Ledger'
			and gl.voucher_no = jv.name 
			and jv.against_bill is not null
			and sii.parent = si.name
			and si.name = jv.against_bill
			and ld.name = acc.master_name %s
		GROUP BY sii.study, jv.against_bill """  % ('%Accounts Payable%',conditions), as_list=1)
