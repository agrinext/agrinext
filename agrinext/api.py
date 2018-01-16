# see license
import frappe
import json
from frappe import _

@frappe.whitelist(allow_guest=True)
def report_error():
	api_access_key = frappe.get_value("AgriNext Settings", None, "guest_access_api_key")
	if frappe.session.user == "Guest":
		if frappe.get_request_header("X-API-KEY") != api_access_key:
			raise frappe.PermissionError

	error_log = frappe.new_doc("Error Log")
	error_log.method = "App Error " + unicode(frappe.utils.datetime.datetime.today())
	error_log.error = unicode(frappe.form_dict)
	error_log.save(ignore_permissions=True)
	return error_log.as_dict()

@frappe.whitelist()
def get_meta(doctype):
	return frappe.get_meta(doctype)
