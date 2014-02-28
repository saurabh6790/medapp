// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

/* toolbar settings */
wn.provide('erpnext.toolbar');

erpnext.toolbar.setup = function() {
	// profile
	var $user = $('#toolbar-user');
	$user.append('<li><a href="#Form/Profile/'+user+'"><i class="icon-fixed-width icon-user"></i> '
		+wn._("My Settings")+'...</a></li>');
	
	if(wn.boot.expires_on || wn.boot.commercial_support) {
		$user.append('<li>\
			<a href="http://www.providesupport.com?messenger=iwebnotes" target="_blank">\
			<i class="icon-fixed-width icon-comments"></i> '+wn._('Live Chat')+'</a></li>');
	}
	
}