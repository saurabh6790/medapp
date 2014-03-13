from __future__ import unicode_literals
import webnotes

def execute(filters=None):
	if not filters: filters ={}
	data = []
	columns = get_columns()
	data = get_data(filters)
	
	return columns,data
def get_data(cond):
	# webnotes.errprint(cond)
	return webnotes.conn.sql(""" SELECT l.name, l.lead_name,
			(SELECT COUNT(*) FROM  `tabPatient Registration` p WHERE l.name=p.referred_by) reff_count,
			(SELECT COUNT(*) FROM  `tabPatient Encounter Entry` e WHERE l.name=e.referrer_name) enc,
			(select sum(basic_charges) from  `tabSales Invoice` si, `tabSales Invoice Item`  sii
			        where sii.parent = si.name  and sii.referrer_name = l.name) total
			FROM
			    tabLead l,
			    tabCampaign cm,
			    `tabSales Invoice` si
			where 
			        l.campaign_name = '%s'
        			and cm.name = l.campaign_name
			        and si.posting_date between '%s' and '%s'
			group by l.name """%(cond.get('campaign'),cond.get('from_date'), cond.get('to_date')),as_list=1)

def get_columns():
	return ['Referrer Id::120','Referrer Name::120','Total Referring Count::140','Total Encountered Count::160','Total Billed  Amount:Currency:120']
