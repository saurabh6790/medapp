# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes
from webnotes.model.doc import Document
from webnotes.utils import flt, fmt_money, cstr, cint
from  selling.doctype.customer.customer import DocType
import datetime
from webnotes import msgprint, _
from selling.doctype.lead.lead import create_contact
class DocType():
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl

	def on_update(self):
		patient_id = None
		from datetime import datetime

		s1=(self.doc.start_time).split(':')
                s2=(self.doc.end_time).split(':')
		date_a=cstr(datetime.combine(datetime.strptime(self.doc.encounter_date,'%Y-%m-%d').date(),datetime.strptime(s1[0]+":"+s1[1],'%H:%M').time()))
                date_b=cstr(datetime.combine(datetime.strptime(self.doc.encounter_date,'%Y-%m-%d').date(),datetime.strptime(s2[0]+":"+s2[1],'%H:%M').time()))
		#webnotes.errprint(self.doc.entry_in_child)
		if self.doc.new_user == 1 and not self.doc.new_patient:
			patient_id = self.make_patient()
			self.doc.new_patient=patient_id
			self.create_new_contact()
			self.create_customer(patient_id)
			self.create_account_head(patient_id)
            		self.doc.save()
		if self.doc.entry_in_child == 'False':
			self.make_child_entry(patient_id)
			#self.make_event()
		if cint(self.doc.checked_in)==1:
                        check_confirmed=webnotes.conn.sql("select true from `tabSlot Child` where slot='"+self.doc.appointment_slot+"' and modality='"+self.doc.encounter+"' and study='"+self.doc.study+"' and date_format(start_time,'%Y-%m-%d %H:%M')=date_format('"+date_a+"','%Y-%m-%d %H:%M') and date_format(end_time,'%Y-%m-%d %H:%M')=date_format('"+date_b+"','%Y-%m-%d %H:%M') and status='Confirm'",debug=1)
			if not check_confirmed:
				webnotes.conn.sql("update tabEvent set event_type='Confirm' where name='%s'"%self.doc.eventid)
                		webnotes.conn.sql("update `tabSlot Child` set status='Confirm' where encounter='%s'"%self.doc.name)
			else:
				webnotes.msgprint("Selected slot is not available",raise_exception=1)

		if not self.doc.eventid:
                	self.create_child()
		else:
			webnotes.conn.sql("update `tabSlot Child` set slot='"+self.doc.appointment_slot+"', start_time='"+cstr(datetime.strptime(date_a,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M'))+"', end_time='"+cstr(datetime.strptime(date_b,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M'))+"' where encounter='"+self.doc.name+"'")
			webnotes.errprint(date_a)
			webnotes.conn.sql("update `tabEvent` set starts_on='"+cstr(datetime.strptime(date_a,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M'))+"', ends_on='"+cstr(datetime.strptime(date_b,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M'))+"' where name='"+self.doc.eventid+"'",debug=1)
	
	
	def create_new_contact(self):
		details = {}
		details['first_name'] = self.doc.first_name
		details['email_id'] = self.doc.email or ''
                details['mobile_no'] = self.doc.mobile or ''
		details['doc']='Customer'
		details['link']=self.doc.name or ''
		create_contact(details)

	def create_customer(self, patient_id):                
                from webnotes.model.doc import Document
                d = Document('Customer')
                d.customer_name = patient_id
                d.full_name = self.doc.first_name
                d.save()

	def get_company_abbr(self):
		return webnotes.conn.get_value('Company', self.doc.company, 'abbr')

	def get_receivables_group(self):
		g = webnotes.conn.sql("select receivables_group from tabCompany where name=%s", self.doc.company)
		g = g and g[0][0] or '' 
		if not g:
			msgprint("Update Company master, assign a default group for Receivables")
			raise Exception
		return g
	
	def create_account_head(self,patient_id):
		if self.doc.company :
			abbr = self.get_company_abbr()
			if not webnotes.conn.exists("Account", (self.doc.name + " - " + abbr)):
				parent_account = self.get_receivables_group()
				# create
				ac_bean = webnotes.bean({
					"doctype": "Account",
					'account_name': patient_id,
					'parent_account': parent_account, 
					'group_or_ledger':'Ledger',
					'company':self.doc.company, 
					'master_type':'Patient Ecounter Entry', 
					'master_name':patient_id,
					"freeze_account": "No"
				})
				ac_bean.ignore_permissions = True
				ac_bean.insert()
				
				webnotes.msgprint(_("Account Head") + ": " + ac_bean.doc.name + _(" created"))
		else :
			webnotes.msgprint(_("Please Select Company under which you want to create account head"))

    	def create_child(self):
		from datetime import datetime
		date_a=cstr(datetime.combine(datetime.strptime(self.doc.encounter_date,'%Y-%m-%d').date(),datetime.strptime(self.doc.start_time,'%H:%M').time()))
		date_b=cstr(datetime.combine(datetime.strptime(self.doc.encounter_date,'%Y-%m-%d').date(),datetime.strptime(self.doc.end_time,'%H:%M').time()))
    		if self.doc.appointment_slot:
			webnotes.errprint([self.doc.start_time])
			check_confirmed=webnotes.conn.sql("select true from `tabSlot Child` where slot='"+self.doc.appointment_slot+"' and modality='"+self.doc.encounter+"' and study='"+self.doc.study+"' and date_format(start_time,'%Y-%m-%d %H:%M')=date_format('"+date_a+"','%Y-%m-%d %H:%M') and date_format(end_time,'%Y-%m-%d %H:%M')=date_format('"+date_b+"','%Y-%m-%d %H:%M') and status='Confirm'",debug=1)
			webnotes.errprint(check_confirmed)
			if not check_confirmed:
				
				check_status=webnotes.conn.sql("select case when count(*)<2 then true else false end  from `tabSlot Child` where slot='"+self.doc.appointment_slot+"' and modality='"+self.doc.encounter+"' and study='"+self.doc.study+"' and date_format(start_time,'%Y-%m-%d %H:%M')=date_format('"+date_a+"','%Y-%m-%d %H:%M') and date_format(end_time,'%Y-%m-%d %H:%M')=date_format('"+date_b+"','%Y-%m-%d %H:%M') and status<>'Cancel'",as_list=1)
				webnotes.errprint(check_status[0][0])
				if check_status[0][0]==1:
					
    					d=Document("Slot Child")
					d.slot=self.doc.appointment_slot
					d.modality=self.doc.encounter
					d.study=self.doc.study
					d.status='Waiting'
    					d.encounter=self.doc.name
    					d.start_time=date_a
    					d.end_time=date_b
					d.save()
					self.make_event(d.name)
					self.doc.slot=d.name
				else:
					webnotes.msgprint("Selected slot is not available",raise_exception=1)
			else:
				webnotes.msgprint("Selected slot is not available",raise_exception=1)
		


	def make_patient(self):
		d = Document('Patient Register')
		d.customer_name = self.doc.first_name + ' ' + self.doc.last_name
		d.mobile = self.doc.phone_number	
		d.company=self.doc.company
		d.save()	
		return d.name
	
	def make_child_entry(self, patient_id=None):
		enct = Document('Encounter')	
		webnotes.errprint([enct, self.doc.patient])
		enct.encounter = self.doc.encounter
		enct.study = self.doc.study
		enct.encounter_date = self.doc.encounter_date
		enct.radiologist_name = self.doc.radiologist_name
		enct.referrer_name = self.doc.referrer_name
		enct.problem_description = self.doc.problem_description
		enct.metal_in = self.doc.metal_in
		enct.pacemaker = self.doc.pacemaker
		enct.claustrophobia = self.doc.claustrophobia
		enct.pregnancy = self.doc.pregnancy
		enct.others = self.doc.others
		enct.procedure_alert = self.doc.procedure_alert
		enct.parent = self.doc.patient if self.doc.patient else patient_id 
		enct.id = self.doc.name
		enct.save(new=1)
		self.doc.entry_in_child = 'True'
		self.doc.save()

	def make_event(self,name_slot):
		evnt = Document('Event')
		evnt.slot=name_slot
		evnt.event_type = 'Waiting'
		evnt.starts_on = self.doc.encounter_date + ' ' +self.doc.start_time
		evnt.ends_on = self.doc.encounter_date + ' ' +self.doc.end_time
		if cint(self.doc.new_user)==1:
			evnt.patient = self.doc.new_patient
			evnt.patient_name= self.doc.first_name + ' ' + self.doc.last_name
		else:
			evnt.patient = self.doc.patient
			evnt.patient_name= self.doc.patient_name
		evnt.service = self.doc.study
		evnt.subject = self.doc.study
		evnt.modality=self.doc.encounter
		evnt.study=self.doc.study
		evnt.save()
		self.doc.eventid = evnt.name
		self.doc.save()
		
		
@webnotes.whitelist()
def get_employee(doctype, txt, searchfield, start, page_len, filters):
	return webnotes.conn.sql("select name, employee_name from tabEmployee where designation = 'Radiologist'")

@webnotes.whitelist()
def update_event(checked, dname,encounter):
		
	if cint(checked) == 1:
		webnotes.conn.sql("update tabEvent set event_type='Confirm' where name='%s'"%dname)
		webnotes.errprint(encounter) 
		webnotes.conn.sql("update `tabSlot Child` set status='Confirm' where encounter='%s'"%encounter)
