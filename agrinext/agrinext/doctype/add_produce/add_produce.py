# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import get_datetime, add_to_date, getdate, nowdate
from frappe.model.document import Document

class AddProduce(Document):
	def autoname(self):
		self.name = self.produce_name

	def validate(self):
		self.set_expiry_date()

	def set_expiry_date(self):
		period = frappe.db.get_value('Item', self.item, "post_harvest_period")
		self.expire_on = add_to_date(get_datetime(self.produced_date), months=period).strftime("%Y-%m-%d")

def disable_expired_produce():
	today = getdate(nowdate())
	frappe.db.sql("""Update `tabAdd Produce`
		set
			disable = 1
		where
			expire_on < '{0}'
	""".format(today))