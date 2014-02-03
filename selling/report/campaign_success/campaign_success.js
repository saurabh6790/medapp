wn.query_reports["Campaign Success"] = {
	"filters": [
		{
			"fieldname":"campaign",
			"label": "Campaign",
			"fieldtype": "Link",
			"options": "Campaign"
		},
		{
			"fieldname":"from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": get_today()
		},
		{
                        "fieldname":"to_date",
                        "label": "To Date",
                        "fieldtype": "Date",
                        "default": get_today()
                }

	]
}
