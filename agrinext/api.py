import frappe, json
import random

from frappe.utils import cint

@frappe.whitelist(allow_guest=True)
def get_otp(mobile_no=None):
	if not mobile_no:
		frappe.throw("NOMOBILE", exc=LookupError)

	u = frappe.db.get_value("User", {"mobile_no": mobile_no}, "name")

	if not u:
		frappe.throw("USERNOTFOUND", exc=LookupError)

	key = mobile_no + "_otp"
	
	# if otp_type == "Numeric":
    otp = ''.join(["{}".format(random.randint(0, 9)) for i in range(0, 6)])
	# elif otp_type == "Alphanumeric":
	# 	otp = frappe.generate_hash(length=otp_length).upper()
	
	otp_json = {"id": key, "otp": otp, "timestamp": str(frappe.utils.get_datetime().utcnow())}
	rs = frappe.cache()
	rs.set_value(key, json.dumps(otp_json))

	#FIRE SMS FOR OTP

	return "OTPGENERATED:{0}".format(otp_json.get("otp"))

@frappe.whitelist(allow_guest=True)
def authenticate_otp(otp=None, mobile_no=None, client_id=None):
	if not otp:
		frappe.throw("NOOTP")

	if not mobile_no:
		frappe.throw("NOMOBILENO")

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

	frappe.local.response = frappe._dict(out)

def create_bearer_token(mobile_no, client_id):
	otoken = frappe.new_doc("OAuth Bearer Token")
	otoken.access_token = frappe.generate_hash(length=30)
	otoken.refresh_token = frappe.generate_hash(length=30)
	otoken.user = frappe.db.get_value("User", {"mobile_no": mobile_no}, "name")
	otoken.scopes = "all openid"
	otoken.client = client_id
	otoken.redirect_uri = frappe.db.get_value("OAuth Client", client_id, "default_redirect_uri")
	otoken.expires_in = 3600
	otoken.save(ignore_permissions=True)
	frappe.db.commit()

	return otoken