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
        "status": "Registered",
        "token_number": token,
        "triage_status": "Waiting"
    })
    pat.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "patient_id": pat.name,
        "token_number": token,
        "full_name": full_name,
        "department": referred_department,
        "visit_type": visit_type,
        "phone": phone
    }

@frappe.whitelist()
def get_today_queue():
    today_start = frappe.utils.today() + " 00:00:00"
    return frappe.db.sql("""
        SELECT name, full_name, phone, referred_department,
               visit_type, status, token_number, triage_status, creation
        FROM `tabPatient Registration`
        WHERE creation >= %s
        ORDER BY token_number ASC
        LIMIT 50
    """, today_start, as_dict=True)

@frappe.whitelist()
def get_today_stats():
    today_start = frappe.utils.today() + " 00:00:00"
    total    = frappe.db.sql("SELECT COUNT(*) FROM `tabPatient Registration` WHERE creation >= %s", today_start)[0][0]
    waiting  = frappe.db.sql("SELECT COUNT(*) FROM `tabPatient Registration` WHERE creation >= %s AND triage_status='Waiting'", today_start)[0][0]
    completed= frappe.db.sql("SELECT COUNT(*) FROM `tabPatient Registration` WHERE creation >= %s AND triage_status='Discharged'", today_start)[0][0]
    return {"registered": total, "waiting": waiting, "completed": completed}

@frappe.whitelist()
def update_patient_status(patient_id, status):
    frappe.db.set_value("Patient Registration", patient_id, "triage_status", status)
    frappe.db.commit()
    return "ok"
