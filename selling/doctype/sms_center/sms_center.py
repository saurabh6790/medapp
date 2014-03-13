# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import webnotes

from webnotes.utils import cstr
from webnotes.model import db_exists
from webnotes.model.bean import copy_doclist
from webnotes.model.code import get_obj
from webnotes import msgprint

  
# ----------

class DocType:
  def __init__(self, doc, doclist=[]):
    self.doc = doc
    self.doclist = doclist
      
  def create_receiver_list(self):
    rec, where_clause = '', ''
    if self.doc.send_to == 'All Customer Contact':
      where_clause = self.doc.customer and " and customer = '%s'" % self.doc.customer or " and ifnull(customer, '') != ''"
    if self.doc.send_to == 'All Supplier Contact':
      where_clause = self.doc.supplier and " and ifnull(is_supplier, 0) = 1 and supplier = '%s'" % self.doc.supplier or " and ifnull(supplier, '') != ''"
    if self.doc.send_to == 'All Sales Partner Contact':
      where_clause = self.doc.sales_partner and " and ifnull(is_sales_partner, 0) = 1 and sales_partner = '%s'" % self.doc.sales_partner or " and ifnull(sales_partner, '') != ''"

    if self.doc.send_to in ['All Contact', 'All Customer Contact', 'All Supplier Contact', 'All Sales Partner Contact']:
      rec = webnotes.conn.sql("select CONCAT(ifnull(first_name,''),'',ifnull(last_name,'')), mobile_no, email_id from `tabContact` where ifnull(mobile_no,'')!='' and docstatus != 2 %s" % where_clause)

    elif self.doc.send_to == 'All Lead (Open)':
      rec = webnotes.conn.sql("select lead_name, mobile_no, email_id from tabLead where ifnull(mobile_no,'')!='' and docstatus != 2 and status = 'Open'")

    elif self.doc.send_to == 'All Employee (Active)':
      where_clause = self.doc.department and " and department = '%s'" % self.doc.department or ""
      where_clause += self.doc.branch and " and branch = '%s'" % self.doc.branch or ""
      rec = webnotes.conn.sql("select employee_name, cell_number, personal_email from `tabEmployee` where status = 'Active' and docstatus < 2 and ifnull(cell_number,'')!='' %s" % where_clause)

    elif self.doc.send_to == 'All Sales Person':
      rec = webnotes.conn.sql("select sales_person_name, mobile_no from `tabSales Person` where docstatus != 2 and ifnull(mobile_no,'')!=''")

    if self.doc.send_to == 'All Patient':
      # webnotes.errprint('all')
      rec = webnotes.conn.sql("select customer_name, ifnull(mobile,0), email from `tabPatient Register` where docstatus != 2 and ifnull(mobile,'')!=''  and ifnull(email,'')!=''")
    if self.doc.send_to == 'Patient':
      rec = webnotes.conn.sql("select customer_name, mobile, email from `tabPatient Register` where docstatus != 2 and ifnull(mobile,'')!='' and ifnull(email,'')!='' and name = '%s'" % self.doc.patient)
    rec_list = ''
    for d in rec:
      rec_list += cstr(d[0]) + ' - ' + cstr(d[1]) + ' - ' + cstr(d[2]) + '\n'
    self.doc.receiver_list = rec_list

  def get_receiver_nos(self):
    receiver_nos = []
    for d in self.doc.receiver_list.split('\n'):
      receiver_no = d
      if '-' in d:
        if self.doc.send_email_sms == 'Sms':
	  if receiver_no.split('-')[1]:
            receiver_no = receiver_no.split('-')[1]
        else:
          if receiver_no.split('-')[2]:
            receiver_no = receiver_no.split('-')[2]

      if receiver_no.strip():
        receiver_nos.append(cstr(receiver_no).strip())
    return receiver_nos

  def send_sms(self):
    if not self.doc.message:
      msgprint("Please enter message before sending")
    else:
      receiver_list = self.get_receiver_nos()
      if receiver_list:
        msgprint(get_obj('SMS Control', 'SMS Control').send_sms(receiver_list, cstr(self.doc.message)))

  def send_email(self):
    if not self.doc.email_body:
       msgprint("Please enter message before sending")

    else:
      receiver_list = self.get_receiver_nos()
      if receiver_list:
        from webnotes.utils.email_lib import sendmail
        sendmail(receiver_list, subject=self.doc.subject, msg = self.doc.email_body)
