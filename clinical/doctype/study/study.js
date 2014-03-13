var a={"study_data":". Study Details","referral_fee_data":". Referral Fee Detail","disc_detail":". Discount Details"};

cur_frm.cscript.refresh=function(doc,cdt,cdn)
{
	setTimeout(function(){
                        for (var key in a)
                        {
                                $('button[data-fieldname='+key+']').css("width","200");
                        }

                },10);
}

cur_frm.cscript.study_data=function(){
	make_linking('study_data')	
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

cur_frm.cscript.referral_fee_data=function(doc,cdt,cdn){
make_linking('referral_fee_data')

}

cur_frm.cscript.disc_detail=function(doc,cdt,cdn){

make_linking('disc_detail')
}


