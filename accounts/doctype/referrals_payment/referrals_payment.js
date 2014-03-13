cur_frm.cscript.commission_rules = function(doc,cdt,cdn) {
	//console.log(cur_frm.fields_dict["payment_details"].get_field("commission_rules"))
	var d = locals[cdt][cdn];
	if(inList(["Fixed Cost"], d.commission_rules)){
		cur_frm.fields_dict["payment_details"].grid.set_column_disp('group', false)
		//df = wn.meta.get_docfield(d.doctype,'group',d.docname).hidden=false?0:1;
		//refresh_field('group', d.name, 'payment_details')
	}
}

cur_frm.cscript.refresh = function(doc, dt,dn){
	if(doc.__islocal) {
		hide_field('make_bank_voucher')
	}	
	else{
		unhide_field('make_bank_voucher')
	}
}

cur_frm.cscript.amount = function(doc,cdt,cdn){
	var d = locals[cdt][cdn];
	d.final_amount = flt(d.amount)
	if(d.commission_rules == 'Percentage'){
		d.final_amount = flt(d.amount) * flt(d.percent);
	}
	refresh_field('final_amount', d.name, 'payment_details') 
	cur_frm.cscript.update_totals(doc)
}

cur_frm.cscript.percent = function(doc, cdt, cdn){
	var d =locals[cdt][cdn];
	d.final_amount = flt(d.amount) 
        if(d.commission_rules == 'Percentage'){
                d.final_amount = flt(d.amount) * (flt(d.percent)/100);
        }
	//d.final_amount = parseFloat(d.amount*(d.percent/100))
	refresh_field('final_amount', d.name, 'payment_details')
	cur_frm.cscript.update_totals(doc);
}

cur_frm.cscript.update_totals = function(doc) {
	var td=0.0; var tc =0.0;
	var el = getchildren('Referrals Payment Details', doc.name, 'payment_details');
	for(var i in el) {
		td += flt(el[i].final_amount, 2);
	}
	var doc = locals[doc.doctype][doc.name];
	doc.total_amount = td
	refresh_many(['total_amount']);
}

/*cur_frm.cscript.make_bank_voucher = function(doc,cdt,cdn){
  	cur_frm.cscript.make_jv(doc, cdt, cdn);
}*/


// Make JV
//-----------------------
cur_frm.cscript.make_jv = function(doc, dt, dn) {
	var call_back = function(r,rt){
		// console.log(r)
		var jv = wn.model.make_new_doc_and_get_name('Journal Voucher');
		jv = locals['Journal Voucher'][jv];
		jv.voucher_type = 'Bank Voucher';
		jv.user_remark = 'Payment of salary for the month: ' + doc.month + 'and fiscal year: ' + doc.fiscal_year;
		jv.fiscal_year = doc.fiscal_year;
		jv.company = doc.company;
		jv.posting_date = dateutil.obj_to_str(new Date());

		// credit to bank
		var d1 = wn.model.add_child(jv, 'Journal Voucher Detail', 'entries');
		d1.account = r.message['def_bank_acc']
		d1.credit = r.message['amount']

		// debit to salary account
		var d2 = wn.model.add_child(jv, 'Journal Voucher Detail', 'entries');
		d2.account = r.message['def_sal_acc'];
		d2.debit = r.message['amount']

		loaddoc('Journal Voucher', jv.name);
	}
	return $c_obj(make_doclist(dt,dn),'get_acc_details','',call_back);
}
