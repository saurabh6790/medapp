# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes
from webnotes.utils import cstr, cint, flt, comma_or, nowdate, get_base_path
import barcode
import os
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
		make_autoname('A'+str(date.today().year)[-2:]+'AA'+'.##')

        def on_update(self):
		webnotes.errprint('in on update')
                self.create_new_contact()
                flag = webnotes.conn.sql("select ifnull(name,'') from tabProfile where name='"+self.doc.email+"'",as_list=1,debug=1)
                if not flag:
                        webnotes.errprint(flag)
                        self.create_profile()
                        self.generate_barcode()
                        self.validate()
                        self.doc.master_type = "Patient Registration"
                        self.create_account_head()
                        self.create_customer()         
                        self.create_patient_encounter_entry()
			self.create_new_contact()
                        webnotes.errprint(self.doc.user_image_show)
                        self.doc.save()

	def create_new_contact(self):
                details = {}
                details['first_name'] = self.doc.customer_name
                details['email_id'] = self.doc.email or ''
                details['mobile_no'] = self.doc.mobile or ''
                create_contact(details)

        def create_customer(self):
                webnotes.errprint('customer creation starts')
                from webnotes.model.doc import Document
                d = Document('Customer')
                d.customer_name = self.doc.name
                d.gender = self.doc.gender
                d.full_name = self.doc.customer_name
                d.save()
                webnotes.errprint(d.name)

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
                self.doc.patient_online_id=self.doc.name
                from barcode.writer import ImageWriter
                ean = barcode.get('code39',self.doc.patient_online_id,writer=ImageWriter())
                path = os.path.join(get_base_path(), "public", "barcode_img")+"/"+self.doc.name
                fullname = ean.save(path)
                barcode_img = '<html>\
                        <table style="width: 100%; table-layout: fixed;">\
                                <tr>\
                                        <td style="width:510px">\
                                                <img src="'"/barcode_img/"+self.doc.name+".png"'" width="200px">\
                                        </td>\
                                </tr>\
                        </table>\
                </html>'
                self.doc.barcode_image = barcode_img

        def create_patient_encounter_entry(self):
                from webnotes.model.bean import getlist
                for encounter in getlist(self.doclist,'encounter_table'):
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

