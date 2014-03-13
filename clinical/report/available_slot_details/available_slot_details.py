from __future__ import unicode_literals
import webnotes
from webnotes.utils import flt
from stock.utils import get_buying_amount
from webnotes import _, msgprint
sql = webnotes.conn.sql

def execute(filters=None):
	if not filters: filters = {}
	import datetime
	from datetime import date,timedelta
	from webnotes.utils import getdate,nowdate,cstr,cint,flt
        dts=datetime.date.today()
	# webnotes.errprint(dts)
	#rs=sql("select start_time from tabSlots")
	#for r in rs:
	#	tt=cstr(r)
	#	webnotes.errprint(tt)
	query = "select name,start_time,end_time,modality,study,active from tabSlots where name not in (SELECT slot FROM `tabSlot Child` where status='Confirm' and start_time in (date_format(sysdate(),'%Y-%m-%d %H:%i')))"
	
	# webnotes.errprint(query)
	res=webnotes.conn.sql(query,as_list=1)
	columns = ["Slot Name:Link/Slots:120","Start Time::120","End Time::120","Modality:Link/Modality:100","Study:Link/Study:100","Active::100"]
	return columns, res

