from __future__ import unicode_literals
import webnotes
from webnotes.model.doc import Document
from webnotes.utils import flt, fmt_money, cstr, cint
from  selling.doctype.customer.customer import DocType
import datetime
from webnotes import msgprint, _
from selling.doctype.lead.lead import create_contact
from webnotes.model.code import get_obj
from webnotes.model.bean import getlist, copy_doclist

def get_encounters():
	encounter_details = webnotes.conn.sql("""select patient, encounter,encounter_date, study, technologist, start_time 
		from `tabPatient Encounter Entry` where encounter_date = DATE_ADD('2014-03-05', INTERVAL 1 DAY)""",as_dict=1)

	for encounter_detail in encounter_details:
		send_notification(encounter_detail)

def send_notification(encounter_detail):
	mail_list = []
	number = []

	msg = """Hi %(patient)s, Your appointment has been schedule on %(encounter_date)s at time %(start_time)s 
		for study %(study)s on modality %(modality)s"""%{'patient': encounter_detail['patient'], 'encounter_date':encounter_detail['encounter_date'], 
		'start_time':encounter_detail['start_time'], 'study':encounter_detail['study'], 'modality':encounter_detail['encounter']}

	technologiest_contact = webnotes.conn.sql("select cell_number, personal_email from tabEmployee where name = '%s'"%(encounter_detail['technologist']),as_list=1)
	patient_contact = webnotes.conn.sql("select mobile, email from `tabPatient Register` where name = '%s'"%(encounter_detail['patient']),as_list=1)

	# webnotes.errprint([technologiest_contact, patient_contact])

	mail_list.append(technologiest_contact[0][1])
	mail_list.append(patient_contact[0][1])

	number.append(technologiest_contact[0][0])
	number.append(patient_contact[0][0])

	send_mail(msg, mail_list)
	send_sms(msg, number)

def send_mail(msg, mail_list):
	from webnotes.utils.email_lib import sendmail
	for id in mail_list:
		if id:
			sendmail(id, subject='Appoiontment Scheduling', msg = msg)

def send_sms(msg, number):
	ss = get_obj('SMS Settings', 'SMS Settings', with_children=1)
	# webnotes.errprint(ss)
	# for num in number:
	# webnotes.errprint(['number',num])
	args = {}
	for d in getlist(ss.doclist, 'static_parameter_details'):
		args[d.parameter] = d.value
	sms_url=webnotes.conn.get_value('SMS Settings', None, 'sms_gateway_url')
	msg_parameter=webnotes.conn.get_value('SMS Settings', None, 'message_parameter')
	receiver_parameter=webnotes.conn.get_value('SMS Settings', None, 'receiver_parameter')
	for num in number:
		if num:
			url = sms_url +"?user="+ args["user"] +"&senderID="+ args["sender ID"] +"&receipientno="+ num +"\
				&dcs="+ args["dcs"]+ "&msgtxt=" + msg +"&state=" +args["state"]
			# webnotes.errprint(url)
			import requests
			r = requests.get(url)
