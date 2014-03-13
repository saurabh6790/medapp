# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes

class DocType:
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl
	
	def on_update(self):
		from accounts.utils import create_advance_entry
		# webnotes.errprint(self.doc.company)
		debit_to = webnotes.conn.sql("select name from tabAccount where master_name='%s'"%self.doc.patient_id,as_list=1)	
		if debit_to:
			create_advance_entry(self.doc.advance_amount, self.doc.patient_id, debit_to[0][0], self.doc.company) 
		else:
			webnotes.msgprint("Account head is not created", raise_exception=1)
