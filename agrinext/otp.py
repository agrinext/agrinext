# Contributors. see license.txt
import frappe, json
import random

from frappe.utils import cint

@frappe.whitelist(allow_guest=True)
def get(mobile_no=None):
	if not mobile_no:
		frappe.throw("NOMOBILE", exc=LookupError)

	u = frappe.db.get_value("User", {"mobile_no": mobile_no}, "name")

	if not u:
		frappe.throw("USERNOTFOUND", exc=LookupError)

	key = mobile_no + "_otp"	
	otp_length = 6 # 6 digit OTP
	otp = ''.join(["{}".format(random.randint(0, 9)) for i in range(0, otp_length)])
	otp_json = {"id": key, "otp": otp, "timestamp": str(frappe.utils.get_datetime().utcnow())}
	rs = frappe.cache()
	rs.set_value(key, json.dumps(otp_json))

	"""
	FIRE SMS FOR OTP
		"{0} is your OTP for AgriNext. Do not share OTP with anybody. Thanks.".format(otp_json.get("otp"))
	"""

	return "OTPGENERATED:{0}".format(otp_json.get("otp")) # MUST DISABLE IN PRODUCTION!!

@frappe.whitelist(allow_guest=True)
def authenticate(otp=None, mobile_no=None, client_id=None):
	if not otp:
		otp = frappe.form_dict.get("otp")
		if not otp:
			frappe.throw("NOOTP")

	if not mobile_no:
		mobile_no = frappe.form_dict.get("mobile_no")
		if not mobile_no:
			frappe.throw("NOMOBILENO")

	if not client_id:
		client_id = frappe.form_dict.get("client_id")
		if not client_id:
			frappe.throw("NOCLIENTID")

	rs = frappe.cache()
	stored_otp = rs.get_value("{0}_otp".format(mobile_no))
	otp_json = json.loads(stored_otp)

	if otp_json.get("otp") != otp:
		frappe.throw("OTPNOTFOUND")

	diff = frappe.utils.get_datetime().utcnow() - frappe.utils.get_datetime(otp_json.get("timestamp"))

	if int(diff.seconds) / 60 >= 10:
		frappe.throw("OTPEXPIRED")

	otoken = create_bearer_token(mobile_no, client_id)
	
	out = {
		"access_token": otoken.access_token,
		"refresh_token": otoken.refresh_token,
		"expires_in": otoken.expires_in,
		"scope": otoken.scopes
	}

	# Delete consumed otp
	rs.delete_key(mobile_no + "_otp")

	frappe.local.response = frappe._dict(out)

def create_bearer_token(mobile_no, client_id):
	otoken = frappe.new_doc("OAuth Bearer Token")
	otoken.access_token = frappe.generate_hash(length=30)
	otoken.refresh_token = frappe.generate_hash(length=30)
	otoken.user = frappe.db.get_value("User", {"mobile_no": mobile_no}, "name")
	otoken.scopes = "all"
	otoken.client = client_id
	otoken.redirect_uri = frappe.db.get_value("OAuth Client", client_id, "default_redirect_uri")
	otoken.expires_in = 3600
	otoken.save(ignore_permissions=True)
	frappe.db.commit()

	return otoken
