// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt"

wn.module_page["Master"] = [
	{
		title: wn._("Documents"),
		top: true,
		icon: "icon-copy",
		items: [
				{
					label: wn._("Inventory Master"),
                    description: wn._("Make Referrals Payments."),
                    doctype:"Item"
				},
				{
                	label: wn._("Study Master"),
                    description: wn._("Make Referrals Payments."),
                    doctype:"Study"
                },                 
                {
                    label: wn._("Modality Master"),
                    description: wn._("Modality Master."),
                    doctype:"Modality"
                },   
		]
	}
]

pscript['onload_master-home'] = function(wrapper) {
	wn.views.moduleview.make(wrapper, "Master");
}