import frappe
from frappe import _

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login"), frappe.PermissionError)
    return context

@frappe.whitelist()
def register_patient(full_name, phone, gender, chief_complaint,
    referred_department, visit_type="OPD", payment_type="Cash",
    date_of_birth=None, blood_group=None, emergency_contact=None,
    emergency_phone=None, address=None):

    # Get token number for today
    today_start = frappe.utils.today() + " 00:00:00"
    token = frappe.db.sql(
        "SELECT COUNT(*) FROM `tabPatient Registration` WHERE creation >= %s",
        today_start)[0][0] + 1

    pat = frappe.get_doc({
        "doctype": "Patient Registration",
        "full_name": full_name,
        "phone": phone,
        "gender": gender,
        "chief_complaint": chief_complaint,
        "referred_department": referred_department,
        "visit_type": visit_type,
        "payment_type": payment_type,
        "date_of_birth": date_of_birth or None,
        "blood_group": blood_group or None,
        "emergency_contact": emergency_contact or None,
        "emergency_phone": emergency_phone or None,
        "address": address or None,
        "status": "Registered"
    })
    pat.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "patient_id": pat.name,
        "token_number": token,
        "full_name": full_name
    }

@frappe.whitelist()
def get_today_queue():
    today_start = frappe.utils.today() + " 00:00:00"
    patients = frappe.db.sql("""
        SELECT name, full_name, phone, referred_department,
               visit_type, status, creation
        FROM `tabPatient Registration`
        WHERE creation >= %s
        ORDER BY creation ASC
        LIMIT 50
    """, today_start, as_dict=True)

    # Add token numbers
    for i, p in enumerate(patients):
        p["token_number"] = i + 1
        p["patient_name"] = p.get("full_name")
        p["department"] = p.get("referred_department")

    return patients

@frappe.whitelist()
def get_today_stats():
    today_start = frappe.utils.today() + " 00:00:00"

    total = frappe.db.sql(
        "SELECT COUNT(*) FROM `tabPatient Registration` WHERE creation >= %s",
        today_start)[0][0]

    waiting = frappe.db.sql(
        "SELECT COUNT(*) FROM `tabPatient Registration` WHERE creation >= %s AND status = 'Registered'",
        today_start)[0][0]

    completed = frappe.db.sql(
        "SELECT COUNT(*) FROM `tabPatient Registration` WHERE creation >= %s AND status = 'Discharged'",
        today_start)[0][0]

    return {
        "registered": total,
        "waiting": waiting,
        "completed": completed
    }
