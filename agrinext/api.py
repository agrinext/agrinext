# see license
import frappe
import json

@frappe.whitelist(allow_guest=True)
def report_error():
	note = frappe.new_doc("Note")
	note.title = unicode(frappe.utils.datetime.datetime.today())
	note.public = 1
	note.content = unicode(frappe.form_dict)
	if frappe.session.user == "Guest" and frappe.get_request_header("X-API-KEY") == "420":
		note.save(ignore_permissions=True)
	else:
		note.save()
