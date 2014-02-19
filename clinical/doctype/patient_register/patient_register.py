# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes

from webnotes.utils import cstr, cint, flt, comma_or, nowdate, get_base_path,today
import barcode
import os
from webnotes import msgprint, _
from datetime import date
from webnotes.model.doc import Document, make_autoname
from  selling.doctype.customer.customer import DocType
from selling.doctype.lead.lead import create_contact

class DocType:
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl
	
	def test_data(self):
                webnotes.errprint("asd")

	def autoname(self):
		#key = 'AA'
		key = webnotes.conn.get_value("LocGlobKey", None, "key")
		curr = webnotes.conn.get_value('Series','A'+str(date.today().year)[-2:]+key,'current')
		if cint(curr)==99:
			key1 = key[0]
			key2 = key[1]
			key2 = key2.replace(key2,chr(ord(key2)+1))
			key = key1 + key2
 			webnotes.conn.set_value("LocGlobKey", "LocGlobKey", "key", key)
                self.doc.patient_local_id = make_autoname('A'+str(date.today().year)[-2:]+key+'.##')

                self.doc.name = self.doc.customer_name + ' ' + self.doc.patient_local_id
		#if(self.doc.name):
		#	self.doc.patient_online_id=cstr(webnotes.conn.sql("select abbr from tabCompany where name=%s", self.doc.company)[0][0])+"/"+cstr(self.doc.lab_branch)+"/"+cstr(self.doc.name)
		dt=today()
		ss="C"+cstr(dt[2:4]+cstr(dt[5:7]))+self.doc.lab_branch[1:]+"-"+key+"-"+''
		key="GID.##"
        	n = ''
		l = key.split('.')
		series_set = False
		doctype=''
		for e in l:
			en = ''
			if e.startswith('#'):
				if not series_set:
					digits = len(e)
					en = self.getseries(n, digits, doctype)
					series_set = True
			else: en = e
			n+=en
		# webnotes.errprint(n[3:])		
		# webnotes.errprint(ss+n[3:])
		self.doc.patient_online_id=ss+n[3:]
		

	def getseries(self,key, digits, doctype=''):				
				
		current = webnotes.conn.sql("select `current` from `tabSeries` where name='GID' for update")
		if current and current[0][0] is not None:
			current = current[0][0]
			webnotes.conn.sql("update tabSeries set current = current+1 where name='GID'")
			current = cint(current) + 1
		else:
			webnotes.conn.sql("insert into tabSeries (name, current) values (GID, 1)")
			current = 1
		return ('%0'+str(digits)+'d') % current

        def on_update(self):
                #lag = webnotes.conn.sql("select ifnull(name,'') from tabProfile where name='"+self.doc.email+"'",as_list=1,debug=1)
		self.check_valid_priority()
		
		check_name=webnotes.conn.sql("select name from `tabCustomer` where name='"+self.doc.customer_name+' '+self.doc.name+"'",as_list=1)
		webnotes.errprint(check_name)
                        
                if not check_name:
                        self.doc.master_type = "Patient Register"
			cust = self.create_customer()
                        self.create_account_head(cust)
                        #self.create_customer()             

                if self.doc.flag=='false':
                        self.create_profile()
                        self.generate_barcode()
                        #self.validate()
			
			self.create_new_contact()
			a=webnotes.conn.sql("select name from `tabEncounter` where parent='"+self.doc.name+"'",as_list=1)        
			if not a:
				webnotes.errprint("hii uygsiuc sdfuksghfui")
                        	self.create_patient_encounter_entry()
                        self.doc.flag='True'
                        self.doc.save()

	def create_new_contact(self):
                details = {}
                details['first_name'] = self.doc.customer_name
                details['email_id'] = self.doc.email or ''
                details['mobile_no'] = self.doc.mobile or ''
		details['link'] = self.doc.name
		details['doc'] = 'Customer'
                create_contact(details)		

	def check_valid_priority(self):
		i=1
		p=s=t=0
		from webnotes.model.bean import getlist
		for d in getlist(self.doclist, 'insurance_table'):
			webnotes.errprint(d.length)
			if d.priority=='Primary ':
				p=p+1
			elif d.priority=='Secondary':
				s+=1
			elif d.priority=='Ternary':
                                t+=1
			if(p>1 or s>1 or t>1):
				webnotes.msgprint(("Duplicate entry found for priority in table  insurance profile at row no '"+cstr(i)+"'."), raise_exception=1)
			
			i+=1
		if i>6 :
			webnotes.msgprint(("Maximum 5 'Insurence Profiles' can be entered. Please remove extra entry(ies)"),raise_exception=1)
		

				

        def create_customer(self):
                webnotes.errprint('customer creation starts')
                from webnotes.model.doc import Document
                d = Document('Customer')
                d.customer_name = self.doc.name
                d.gender = self.doc.gender
                d.full_name = self.doc.customer_name
                d.save()
                return d.name

        def create_account_head(self, cust):
                if self.doc.company :
                        abbr = webnotes.conn.get_value('Company', self.doc.company, 'abbr')

                        if not webnotes.conn.sql("select name from tabAccount where name=%s", (self.doc.name + " - " + abbr)):
                                ac_bean = webnotes.bean({
                                        "doctype": "Account",
                                        'account_name': cust,
                                        'parent_account': "Accounts Receivable - " + abbr,
                                        'group_or_ledger':'Ledger',
                                        'company': self.doc.company,
                                        'account_type': '',
                                        'tax_rate': '0',
                                        'master_type': 'Patient Register',
                                        'master_name': self.doc.name,
                                        "freeze_account": "No"
                                })
                                ac_bean.ignore_permissions = True
                                ac_bean.insert()

                                webnotes.msgprint(_("Created Account Head: ") + ac_bean.doc.name)
                else :
                        webnotes.msgprint("Please select Company under which you want to create account head")



        def create_profile(self):
                profile = webnotes.bean({
                        "doctype":"Profile",
                        "email": self.doc.email,
                        "first_name": self.doc.customer_name,
                        "user_image":self.doc.user_image,
                        "enabled": 1,
                        "user_type": "Customer"
                })
                profile.ignore_permissions = True
                profile.insert()

        def generate_barcode(self):
                webnotes.errprint([self.doc.naming_series])
                # self.doc.patient_online_id=self.doc.name
                # from barcode.writer import ImageWriter
                # ean = barcode.get('code39','123322ABS232')
                # webnotes.errprint(ean)
                # path = os.path.join(get_base_path(), "public", "barcode_img")+"/"+self.doc.name
                # fullname = ean.save(path)
                # barcode_img = '<html>\
                #         <table style="width: 100%; table-layout: fixed;">\
                #                 <tr>\
                #                         <td style="width:510px">\
                #                                 <img src="'"/barcode_img/"+self.doc.name+".png"'" width="200px">\
                #                         </td>\
                #                 </tr>\
                #         </table>\
                # </html>'
                #s="23232ASA343222"
                s=self.doc.name
                import barcode
                from barcode.writer import ImageWriter
                ean = barcode.get('code39', s, writer=ImageWriter())
                path = os.path.join(get_base_path(), "public", "barcode_img")+"/"+s
                filename = ean.save(path)
                barcode_img = '<html>\
                         <table style="width: 100%; table-layout: fixed;">\
                                 <tr>\
                                         <td style="width:510px">\
                                                 <img src="'"../barcode_img/"+s+".png"'" width="200px">\
                                         </td>\
                                 </tr>\
                         </table>\
                 </html>'
                self.doc.barcode_image = barcode_img
                self.doc.save()

        def create_patient_encounter_entry(self):
                from webnotes.model.bean import getlist
                for encounter in getlist(self.doclist,'encounter_table'):
			if encounter:
                        	enct = Document('Patient Encounter Entry')
                        	enct.encounter = encounter.encounter
                        	enct.encounter_date = encounter.encounter_date
                        	enct.radiologist_name = encounter.radiologist_name
                        	enct.referrer_name = encounter.referrer_name
                        	enct.problem_description = encounter.problem_description
                        	enct.metal_in = encounter.metal_in
                        	enct.pacemaker = encounter.pacemaker
                        	enct.claustrophobia = encounter.claustrophobia
                        	enct.pregnancy = encounter.pregnancy
                        	enct.others = encounter.others
                        	enct.procedure_alert = encounter.procedure_alert
                        	enct.patient = encounter.parent
                        	enct.entry_in_child = 'True'
                        	enct.save()
                        	webnotes.conn.sql("update tabEncounter set id = '%s' where name = '%s'"%(enct.name,encounter.name))
	
