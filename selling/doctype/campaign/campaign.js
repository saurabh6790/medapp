// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

 

//--------- ONLOAD -------------
cur_frm.cscript.onload = function(doc, cdt, cdn) {
if(this.frm.doc.__islocal) {
doc.date=get_today();
}
}
cur_frm.cscript.refresh = function(doc, cdt, cdn) {
  
}
