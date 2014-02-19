 // Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt"

wn.module_page["Clinical"] = [
        {
                top: true,
                title: wn._("Documents"),
                icon: "icon-copy",
                items: [
			{
                                label: wn._("Patient Registration"),
                                description: wn._("Patient Registration form."),
                                doctype:"Patient Register"
                        },

                  
                        {
                                label: wn._("Patient Encounter Entry"),
                                description: wn._("Make Patient Encounter Entry"),
                                doctype:"Patient Encounter Entry"
                        },                                              
                        {
                                label: wn._("Appoinment Details"),
                                description: wn._("Appoinment Details"),
                                doctype:"Event"
                        },                      
			{
                                label: wn._("Study Master"),
                                description: wn._("Make Referrals Payments."),
                                doctype:"Study"
                        },                       
                        
                        {
                                label: wn._("Modality"),
                                description: wn._("Modality Master."),
                                doctype:"Modality"
                        },
                        {
                                label: wn._("Slot Master"),
                                description: wn._("Slot Master."),
                                doctype:"Slots"
                        },                        

                        {
                                "label":wn._("Slot Details Report"),
                                route: "query-report/Available%20Slot%20Details",
                                doctype: "Slots"
                        },     
                        {
                                "label":wn._("Advance Payment"),
                                doctype: "Advance Entry"
                        },                

                ]
        }/*,
        {
                title: wn._("Masters"),
                icon: "icon-book",
                items: [
                        {
                                label: wn._("Contact"),
                                description: wn._("All Contacts."),
                                doctype:"Contact"
                        },
                ]
        },
        {
                title: wn._("Setup"),
                icon: "icon-cog",
                items: [
                        {
                                "label": wn._("Selling Settings"),
                                "route": "Form/Selling Settings",
                                "doctype":"Selling Settings",
                                "description": wn._("Settings for Selling Module")
                        },
                ]
        }*/
]

pscript['onload_clinical-home'] = function(wrapper) {
        wn.views.moduleview.make(wrapper, "Clinical");
}
