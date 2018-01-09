# see license
import frappe
import json

@frappe.whitelist()
def report_error():
	if(frappe.get_request_header("X-API-KEY") == "420"):
		note = frappe.new_doc("Note")
		note.title = unicode(frappe.utils.datetime.datetime.today())
		note.public = 1
		note.content = unicode(frappe.form_dict)
		note.save(ignore_permissions=True)
