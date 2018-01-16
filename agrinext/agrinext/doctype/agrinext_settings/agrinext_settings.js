// Copyright (c) 2018, Frappé and contributors
// For license information, please see license.txt

frappe.ui.form.on('AgriNext Settings', {
	refresh(frm) {
		frm.add_custom_button(__('Generate Guest Key'), () => {
			frappe.confirm(
				__("Apps using current key won't be able to access API, are you sure?"),
				() => {					
					frappe.call({
						type:"POST",
						method:"agrinext.agrinext.doctype.agrinext_settings.agrinext_settings.generate_guest_key",
					}).done(r=>frm.reload_doc())
					.fail(r=>frappe.msgprint(__("Could not generate API Key")));
				}
			)
		});
	}
});
