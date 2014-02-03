# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import webnotes
from webnotes.model.doc import Document
from  selling.doctype.lead.lead import DocType
from webnotes import msgprint, _
from selling.doctype.lead.lead import create_contact
class DocType():
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl
	
	def on_submit(self):
		self.create_lead()
	
	def create_lead(self):
                from webnotes.model.bean import getlist
                for attendee in getlist(self.doclist,'campaign_attendees'):
			lead = Document('Lead')
			lead.salutation = attendee.salutation
			lead.lead_name = attendee.attendee_name
			lead.specialty = attendee.speciality
			lead.company_name = attendee.organization_name
			lead.email_id = attendee.email_id
			lead.phone = attendee.phone
			lead.mobile_no = attendee.mobile_no
			lead.campaign_name = self.doc.name
			lead.save()
			self.create_new_contact(attendee,lead.name)
			self.create_account_head(lead.name)

	def create_new_contact(self, attendee,lead_name):
		details = {}
		details['first_name'] = attendee.attendee_name
		details['email_id'] = attendee.email_id or ''
		details['mobile_no'] = attendee.mobile_no or ''
		details['link']=lead_name
		details['doc'] ='Lead'
		create_contact(details)
		

	def create_account_head(self, lead_name):
                if self.doc.company :
                        abbr = webnotes.conn.get_value('Company', self.doc.company, 'abbr')

                        if not webnotes.conn.sql("select name from tabAccount where name=%s", (lead_name + " - " + abbr)):
                                ac_bean = webnotes.bean({
                                        "doctype": "Account",
                                        'account_name': lead_name,
                                        'parent_account': "Accounts Payable - " + abbr,
                                        'group_or_ledger':'Ledger',
                                        'company': self.doc.company,
                                        'account_type': '',
                                        'tax_rate': '0',
                                        'master_type': 'Lead',
                                        'master_name': lead_name,
                                        "freeze_account": "No"
                                })
                                ac_bean.ignore_permissions = True
                                ac_bean.insert()

                                webnotes.msgprint(_("Created Account Head: ") + ac_bean.doc.name)
                else :
                        webnotes.msgprint("Please select Company under which you want to create account head")
		
