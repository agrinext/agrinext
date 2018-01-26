# see license
import frappe
import json
from frappe import _
from frappe.utils.file_manager import save_file

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

@frappe.whitelist()
def upload_file():
	'''Upload a file (POST)

	:param filename: filename e.g. test-file.txt
	:param filedata: base64 encode filedata
	:param doctype: Reference DocType to attach file
	:param docname: Reference DocName to attach file
	:param folder: Folder to add File into
	:param decode: decode filedata from base64 encode
	:param is_private: Attach file as private file
	:param docfield: file to attach to'''

	filename = frappe.form_dict.get("filename")
	filedata = frappe.form_dict.get("filedata")
	doctype = frappe.form_dict.get("doctype")
	docname = frappe.form_dict.get("docname")
	folder = frappe.form_dict.get("folder")
	decode = frappe.form_dict.get("decode")
	is_private = frappe.form_dict.get("is_private")
	docfield = frappe.form_dict.get("docfield")

	if not frappe.has_permission(doctype):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	f = save_file(filename, filedata, doctype, docname, folder, decode, is_private, docfield)

	if docfield and doctype:
		doc = frappe.get_doc(doctype, docname)
		doc.set(docfield, f.file_url)
		doc.save()

	return f.as_dict()
