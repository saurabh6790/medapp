cur_frm.get_field("modality").get_query=function(doc,cdt,cdn)
{
   return "select name from `tabModality` where active='Yes'"
}

cur_frm.get_field("study").get_query=function(doc,cdt,cdn)
{
   return "select name from `tabStudy` where modality='"+doc.modality+"'"
}

