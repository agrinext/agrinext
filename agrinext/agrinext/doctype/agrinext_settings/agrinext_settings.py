# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AgriNextSettings(Document):
	pass

@frappe.whitelist()
def generate_guest_key():
	agrinext_settings = frappe.get_doc("AgriNext Settings", None)
	agrinext_settings.guest_access_api_key = frappe.generate_hash()
	agrinext_settings.save()
