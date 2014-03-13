cur_frm.cscript.user_image = function(doc) {
        refresh_field("user_image_show");
}

cur_frm.cscript.encounter_table_add=function(doc,cdt,cdn){
        var d = locals[cdt][cdn];
        if(doc.referred_by)
        {
        d.referrer_name=doc.referred_by
        }
}

cur_frm.fields_dict.encounter_table.grid.get_field("radiologist_name").get_query = function(doc,cdt,cdn) {
        return{ query:"selling.doctype.patient_encounter_entry.patient_encounter_entry.get_employee"}
}

cur_frm.add_fetch('radiologist_name', 'employee_name', 'radiologist_');
cur_frm.add_fetch('referrer_name', 'lead_name', 'referral');


cur_frm.add_fetch('referred_by','lead_name','contact_name');
cur_frm.cscript.refresh = function(doc, cdt, cdn){
//
//        var cl = getchildren('Insurance Profile', doc.name, 'insurance_table');
//        //console.log(cl)
//
//        //console.log(cl.length);
//
//        if(cl.length>5)
//                msgprint("Sorry..!! Only Five Records can be added in insurance table");
//        else
//
//                var arr= new Array();
//
//                for(i=0;i<cl.length;i++){
//
//
//                        for(j=0;j<arr.length;j++){
//                                //console.log(cl[i].priority == arr[j]);
//                                if(cl[i].priority == arr[j]){
//                                        console.log("in if loop");
//						
//                                        msgprint("Duplicate Priority at Row Number "+(i+1)+" where Short Description is '"+cl[i].short_description+"'");
//                                }
//                                else
//                                {
//                                        console.log("in else loop");
//
//                                }
//                   }
//                arr.push(cl[i].priority);
//
//                }
//refresh_field('insurance_table');
//
//        setTimeout(function(){
//                        for (var key in a)
//                        {
//                                $('button[data-fieldname='+key+']').css("width","200");
//                        }
//
//               },10);
// console.log("form refreshed ");
	//if(doc.__islocal && !doc.lab_branch) {
	// doc.lab_branch='B0001'
	//}
}

var a={"general_information":". General Information","additional_information":". Additional Iformation","insurance_profile_data":". Insurance Profile","encounters_data":". Encounters"};


cur_frm.cscript.general_information=function(doc,cdt,cdn){
make_linking('general_information')

}
cur_frm.fields_dict['state'].get_query = function(doc) {
 return "select name from tabState where country='"+doc.country+"'"
}

cur_frm.fields_dict['state_1'].get_query = function(doc) {
 return "select name from tabState where country='"+doc.country_1+"'"
}


function make_linking(show_key){

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

        }

cur_frm.cscript.additional_information=function(doc,cdt,cdn){
make_linking('additional_information')

}

cur_frm.cscript.insurance_profile_data=function(doc,cdt,cdn){

make_linking('insurance_profile_data')
}

cur_frm.cscript.encounters_data=function(doc,cdt,cdn){
make_linking('encounters_data')

}

cur_frm.cscript.title=function(doc,cdt,cdn){
        get_server_fields('test_data','','',doc,cdt,cdn,1)
}

