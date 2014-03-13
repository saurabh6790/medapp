// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

wn.require('app/utilities/doctype/sms_control/sms_control.js');
wn.require('app/setup/doctype/contact_control/contact_control.js');

wn.provide("erpnext");
var a={"referring_physician_details":". Referring Physician Details","communication":". Communication","address_and_contact":". Address & Contact","referral_fee":". Referral Fee"};
erpnext.LeadController = wn.ui.form.Controller.extend({
	setup: function() {
		this.frm.fields_dict.customer.get_query = function(doc,cdt,cdn) {
				return { query:"controllers.queries.customer_query" } }
	},
	
	onload: function() {
		if(cur_frm.fields_dict.lead_owner.df.options.match(/^Profile/)) {
			cur_frm.fields_dict.lead_owner.get_query = function(doc,cdt,cdn) {
				return { query:"selling.doctype.lead.lead.get_lead_owner" } }
		}

		if(cur_frm.fields_dict.contact_by.df.options.match(/^Profile/)) {
			cur_frm.fields_dict.contact_by.get_query = function(doc,cdt,cdn) {
				return { query:"core.doctype.profile.profile.profile_query" } }
		}

		if(in_list(user_roles,'System Manager')) {
			cur_frm.footer.help_area.innerHTML = '<p><a href="#Form/Sales Email Settings">'+wn._('Sales Email Settings')+'</a><br>\
				<span class="help">'+wn._('Automatically extract Leads from a mail box e.g.')+' "sales@example.com"</span></p>';
		}
	},
	
	refresh: function() {
		var doc = this.frm.doc;
		erpnext.hide_naming_series();
		this.frm.clear_custom_buttons();

		this.frm.__is_customer = this.frm.__is_customer || this.frm.doc.__is_customer;
		if(!this.frm.doc.__islocal && !this.frm.doc.__is_customer) {
			this.frm.add_custom_button(wn._("Create Customer"), this.create_customer);
			this.frm.add_custom_button(wn._("Create Opportunity"), this.create_opportunity);
			this.frm.appframe.add_button(wn._("Send SMS"), this.frm.cscript.send_sms, "icon-mobile-phone");
		}
		
		cur_frm.communication_view = new wn.views.CommunicationList({
			list: wn.model.get("Communication", {"parenttype": "Lead", "parent":this.frm.doc.name}),
			parent: this.frm.fields_dict.communication_html.wrapper,
			doc: this.frm.doc,
			recipients: this.frm.doc.email_id
		});
		
		if(!this.frm.doc.__islocal) {
			this.make_address_list();
		}
		
		setTimeout(function(){
			for (var key in a)
	                {
				$('button[data-fieldname='+key+']').css("width","200");
			}

		},10);
		//this.make_linking('referring_physician_details')
	},

	referring_physician_details:function(){
		this.make_linking('referring_physician_details')
		
	},

	make_linking:function(show_key){
			
		for (var key in a)
		{
			// console.log("hi")		
			$('button[data-fieldname='+key+']').css("width","200");
			if(key==show_key)
			{
				$(".row:contains('"+a[key]+"')").show()
			}
			else
			{
				$(".row:contains('"+a[key]+"')").hide()
			}
		}
	
	},

	communication:function(){
                this.make_linking('communication')
        },

	address_and_contact:function(){
                this.make_linking('address_and_contact')
        },

	referral_fee:function(){
                this.make_linking('referral_fee')
        },
	
	make_address_list: function() {
		var me = this;
		if(!this.frm.address_list) {
			this.frm.address_list = new wn.ui.Listing({
				parent: this.frm.fields_dict['address_html'].wrapper,
				page_length: 5,
				new_doctype: "Address",
				get_query: function() {
					return 'select name, address_type, address_line1, address_line2, \
					city, state, country, pincode, fax, email_id, phone, \
					is_primary_address, is_shipping_address from tabAddress \
					where lead="'+me.frm.doc.name+'" and docstatus != 2 \
					order by is_primary_address, is_shipping_address desc'
				},
				as_dict: 1,
				no_results_message: wn._('No addresses created'),
				render_row: this.render_address_row,
			});
			// note: render_address_row is defined in contact_control.js
		}
		this.frm.address_list.run();
	}, 
	
	create_customer: function() {
		wn.model.open_mapped_doc({
			method: "selling.doctype.lead.lead.make_customer",
			source_name: cur_frm.doc.name
		})
	}, 
	
	create_opportunity: function() {
		wn.model.open_mapped_doc({
			method: "selling.doctype.lead.lead.make_opportunity",
			source_name: cur_frm.doc.name
		})
	}
});


$.extend(cur_frm.cscript, new erpnext.LeadController({frm: cur_frm}));

cur_frm.fields_dict['physician_values'].grid.get_field('modality').get_query = function(doc, cdt, cdn) {
        var d = locals[cdt][cdn];
        return "select name from `tabModality` where active='Yes'"
}

cur_frm.fields_dict['state'].get_query = function(doc) {
 return "select name from tabState where country='"+doc.country+"'"
}


