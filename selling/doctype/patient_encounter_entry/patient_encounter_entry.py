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
from selling.doctype.patient_encounter_entry.notification_schedular import get_encounters
class DocType():
        def __init__(self, d, dl):
                self.doc, self.doclist = d, dl

        def on_update(self):
                patient_id = None
                from datetime import datetime

                if self.doc.status == 'Canceled':
                        webnotes.conn.sql("update `tabPatient Encounter Entry` set docstatus = '1' where name = '%s'"%(self.doc.name))

                s1=(self.doc.start_time).split(':')
                s2=(self.doc.end_time).split(':')
                # date_a=cstr(datetime.combine(datetime.strptime(self.doc.encounter_date,'%Y-%m-%d').date(),datetime.strptime(s1[0]+":"+s1[1],'%H:%M').time()))
                # date_b=cstr(datetime.combine(datetime.strptime(self.doc.encounter_date,'%Y-%m-%d').date(),datetime.strptime(s2[0]+":"+s2[1],'%H:%M').time()))
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

                if not self.doc.eventid:
                        self.create_child()
                else:
                        webnotes.conn.sql("update `tabSlot Child` set slot='"+self.doc.appointment_slot+"', start_time='"+cstr(datetime.strptime(date_a,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M'))+"', end_time='"+cstr(datetime.strptime(date_b,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M'))+"' where encounter='"+self.doc.name+"'")
                        # webnotes.errprint(date_a)
                        webnotes.conn.sql("update `tabEvent` set starts_on='"+cstr(datetime.strptime(date_a,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M'))+"', ends_on='"+cstr(datetime.strptime(date_b,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M'))+"' where name='"+self.doc.eventid+"'")

                if cint(self.doc.checked_in)==1: pass
                        # check_confirmed=webnotes.conn.sql("select true from `tabSlot Child` where slot='"+self.doc.appointment_slot+"' and modality='"+self.doc.encounter+"' and study='"+self.doc.study+"' and date_format(start_time,'%Y-%m-%d %H:%M')=date_format('"+date_a+"','%Y-%m-%d %H:%M') and date_format(end_time,'%Y-%m-%d %H:%M')=date_format('"+date_b+"','%Y-%m-%d %H:%M') and status='Confirm'",debug=1)
                        # if not check_confirmed:
                        #         webnotes.conn.sql("update tabEvent set event_type='Confirm' where name='%s'"%self.doc.eventid)
                        #         webnotes.conn.sql("update `tabSlot Child` set status='Confirm' where encounter='%s'"%self.doc.name)
                        # else:
                        #         webnotes.msgprint("Selected slot is not available",raise_exception=1)
                # get_encounters()
                # self.send_notification()

        def send_notification(self):
                mail_list = []
                number = []

                msg = """Hi %(patient)s, Your appointment has been schedule on %(encounter_date)s at time %(start_time)s 
                        for study %(study)s on modality %(modality)s"""%{'patient': self.doc.patient, 'encounter_date':self.doc.encounter_date, 
                        'start_time':self.doc.start_time, 'study':self.doc.study, 'modality':self.doc.modality}

                technologiest_contact = webnotes.conn.sql("select cell_number, personal_email from tabEmployee where name = '%s'"%(self.doc.technologist),as_list=1)
                patient_contact = webnotes.conn.sql("select mobile, email from `tabPatient Register` where name = '%s'"%(self.doc.patient),as_list=1)

                # webnotes.errprint([technologiest_contact, patient_contact])

                mail_list.append(technologiest_contact[0][1])
                mail_list.append(patient_contact[0][1])

                number.append(technologiest_contact[0][0])
                number.append(patient_contact[0][0])

                self.send_mail(msg, mail_list)
                self.send_sms(msg, number)

        def send_mail(self, msg, mail_list):
                from webnotes.utils.email_lib import sendmail
                for id in mail_list:
                        if id:
                                sendmail(id, subject='Appoiontment Scheduling', msg = msg)

        def send_sms(self, msg, number):
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
                # date_a=cstr(datetime.combine(datetime.strptime(self.doc.encounter_date,'%Y-%m-%d').date(),datetime.strptime(self.doc.start_time,'%H:%M').time()))
                # date_b=cstr(datetime.combine(datetime.strptime(self.doc.encounter_date,'%Y-%m-%d').date(),datetime.strptime(self.doc.end_time,'%H:%M').time()))
                if self.doc.appointment_slot:
                        # webnotes.errprint([self.doc.start_time])
                        check_confirmed=webnotes.conn.sql("select true from `tabSlot Child` where slot='"+self.doc.appointment_slot+"' and modality='"+self.doc.encounter+"' and study='"+self.doc.study+"' and date_format(start_time,'%Y-%m-%d %H:%M')=date_format('"+date_a+"','%Y-%m-%d %H:%M') and date_format(end_time,'%Y-%m-%d %H:%M')=date_format('"+date_b+"','%Y-%m-%d %H:%M') and status='Confirm'")
                        # webnotes.errprint(check_confirmed)
                        if not check_confirmed:

                                check_status=webnotes.conn.sql("select case when count(*)<2 then true else false end  from `tabSlot Child` where slot='"+self.doc.appointment_slot+"' and modality='"+self.doc.encounter+"' and study='"+self.doc.study+"' and date_format(start_time,'%Y-%m-%d %H:%M')=date_format('"+date_a+"','%Y-%m-%d %H:%M') and date_format(end_time,'%Y-%m-%d %H:%M')=date_format('"+date_b+"','%Y-%m-%d %H:%M') and status<>'Cancel'",as_list=1)
                                # webnotes.errprint(check_status[0][0])
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

        def child_entry(self,patient_data):  
                services = webnotes.conn.sql(""" SELECT foo.*, case when exists(select true from `tabPhysician Values` a WHERE a.study_name=foo.study AND a.parent=foo.referrer_name and a.referral_fee <> 0) then (select a.referral_fee from `tabPhysician Values` a WHERE a.study_name=foo.study AND a.parent=foo.referrer_name) else (select ifnull(referral_fee,0) from tabStudy where name=foo.study) end as referral_fee,
case when exists(select true from `tabPhysician Values` a WHERE a.study_name=foo.study AND a.parent=foo.referrer_name and a.referral_fee <> 0) then (select a.referral_rule from `tabPhysician Values` a WHERE a.study_name=foo.study AND a.parent=foo.referrer_name) else (select referral_rule from tabStudy where name=foo.study) end as referral_rule
        FROM ( SELECT s.study_aim AS study,s.modality, e.encounter,e.referrer_name, e.name, s.discount_type,s.study_detials,s.discounted_value as dis_value FROM `tabEncounter` e, tabStudy s WHERE ifnull(e.is_invoiced,'False')='False' AND 
e.parent ='%s' and s.name = e.study) AS foo"""%(patient_data),as_dict=1)
                
                patient_data_new=[]
                # webnotes.errprint(services)
                tot_amt = 0.0
                for srv in services:
                                
                        # cld = addchild(self.doc, 'entries', 'Sales Invoice Item',self.doclist)          
                        # cld.study = srv['study']
                        # cld.modality = srv['modality']
                        # cld.encounter_id = srv['name']
                        # cld.discount_type = srv['discount_type']
                        export_rate=webnotes.conn.sql("""select study_fees from tabStudy where name = '%s' """%srv['study'],as_list=1)
                        srv['export_rate'] = export_rate[0][0] if export_rate else 0
                        # cld.referrer_name=srv['referrer_name']
                        if srv['referrer_name']:
                                acc_head = webnotes.conn.sql("""select name from `tabAccount` where master_name='%s'"""%(srv['referrer_name']))
                                if acc_head and acc_head[0][0]:
                                        srv['referrer_physician_credit_to'] = acc_head[0][0]
                                
                        # cld.referral_rule= srv['referral_rule']
                        # cld.referral_fee= srv['referral_fee']
                        if srv['discount_type']=='Regular discount':
                                # cld.discount=srv['dis_value']
                                srv['basic_charges']=cstr(flt(srv['export_rate']-flt(flt(srv['export_rate'])*flt(srv['dis_value'])/100)))
                                srv['discount_in_amt']=cstr(flt(flt(srv['export_rate'])*flt(srv['dis_value'])/100))
                        else:
                                if srv['referral_rule'] == 'Fixed Cost':
                                        srv['basic_charges']=cstr(flt(srv['export_rate'])-flt(srv['referral_fee']))                              
                                        srv['discount_in_amt']=cstr(srv['referral_fee'])
                                else:       
                                        srv['basic_charges']=cstr(flt(srv['export_rate']) - (flt(srv['export_rate'])*(flt(srv['referral_fee'])/100)))
                                        srv['dis_value'] = cstr(srv['referral_fee']) 
                                #cld.discount=cstr(round(flt(cld.referral_fee)/flt(cld.export_rate)*100,2))
                        
                        # cld.description=srv['study_detials']    
                        # cld.qty=1
                        tot_amt = flt(srv['basic_charges']) + tot_amt
                        srv['amount'] = tot_amt
                        patient_data_new.append(srv)
                # webnotes.errprint(patient_data_new)
                return patient_data_new

        def make_child_entry(self, patient_id=None):
                enct = Document('Encounter')
                # webnotes.errprint([enct, self.doc.patient])
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
def get_patient(doctype, txt, searchfield, start, page_len, filters):
        return webnotes.conn.sql("""select name, first_name from `tabPatient Register` 
                where docstatus < 2 
                        and (%(key)s like "%(txt)s" 
                                or first_name like "%(txt)s") 
                order by 
                        case when name like "%(txt)s" then 0 else 1 end, 
                        case when first_name like "%(txt)s" then 0 else 1 end, 
                        name 
                limit %(start)s, %(page_len)s""" % {'key': searchfield, 'txt': "%%%s%%" % txt,
                'start': start, 'page_len': page_len})
        
@webnotes.whitelist()
def update_event(checked, dname,encounter):

        if cint(checked) == 1:
                webnotes.conn.sql("update tabEvent set event_type='Confirm' where name='%s'"%dname)
                # webnotes.errprint(encounter)
                webnotes.conn.sql("update `tabSlot Child` set status='Confirm' where encounter='%s'"%encounter)

@webnotes.whitelist()
def get_events(start, end, doctype,op,filters=None):
        # webnotes.errprint(['hello',doctype, op])
        cnd =''
        if op:
                cnd = "and encounter = '%(pros)s'"%{"pros":op}

        from webnotes.widgets.reportview import build_match_conditions
        #if not webnotes.has_permission("Task"):
        #        webnotes.msgprint(_("No Permission"), raise_exception=1)
        conditions = ''
        # conditions = build_match_conditions("Patient Encounter Entry")
        # conditions and (" and " + conditions) or ""
        
        if filters:
                filters = json.loads(filters)
                for key in filters:
                        if filters[key]:
                                conditions += " and " + key + ' = "' + filters[key].replace('"', '\"') + '"'
        
        data = webnotes.conn.sql("""select name, start_time, end_time, 
                study, status,encounter from `tabPatient Encounter Entry`
                where  ((start_time between '%(start)s' and '%(end)s') \
                        or (end_time between '%(start)s' and '%(end)s')) %(cnd)s 
                %(conditions)s""" % {
                        "start": start,
                        "end": end,
                        "conditions": conditions,
                        "cnd":cnd
                }, as_dict=True, update={"allDay": 0})

        return data

@webnotes.whitelist()
def get_modality():
        return webnotes.conn.sql("select name from tabModality", as_list=1)

@webnotes.whitelist()
def set_slot(modality, start_time, end_time):
        time = get_modality_time(modality)
        if cint(time) > 30:
                start_time = calc_start_time(start_time, modality)
        end_time = calc_end_time(cstr(start_time),time)
        start_time, end_time = check_availability(modality, start_time, end_time, time)
        
        return start_time, end_time

def check_availability(modality, start_time, end_time, time):
        # webnotes.errprint(start_time)
        count = webnotes.conn.sql("""select sum(case when status = 'Waiting' then 2 when status = 'Confirmed' then 1 else 0 end) as status from `tabPatient Encounter Entry` 
                where encounter = '%(encounter)s' and start_time = '%(start_time)s' and end_time = '%(end_time)s'
                """%{'encounter':modality, 'start_time':start_time, 'end_time':end_time},as_list=1)

        if count[0][0] in (1, 4, 3):
                # webnotes.errprint("if loop")
                start_time = end_time
                end_time = calc_end_time(cstr(start_time),time)

                return check_availability(modality, start_time, end_time, time)

        else:
                # webnotes.errprint(["else loop", start_time, end_time])
                return start_time, end_time


def get_modality_time(modality):
        return webnotes.conn.get_value('Modality',modality,'time_required')

def calc_end_time(start_time,time):
        import datetime
        now = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_time = now + datetime.timedelta(minutes=cint(time))
        return end_time

def calc_start_time(start_time, modality):
        end_slot = datetime.datetime.strptime(cstr(start_time), '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=30)
        start_time_list = webnotes.conn.sql("""select end_time from `tabPatient Encounter Entry` 
                        where encounter='%(encounter)s' and end_time between '%(start_time)s' 
                                and '%(end_slot)s'"""%{'encounter':modality, 'start_time':start_time, 'end_slot':end_slot})
        if start_time_list:
                start_time = start_time_list[0][0]
        
        return start_time

@webnotes.whitelist()
def get_patient(patient_id):
        get_obj('DB SYNC', 'DB SYNCl').sync_db(patient_id)