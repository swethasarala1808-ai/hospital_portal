import frappe
from frappe import _

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login"), frappe.PermissionError)
    context.csrf_token = frappe.sessions.get_csrf_token()
    return context

@frappe.whitelist()
def register_patient(full_name, phone, gender, chief_complaint, referred_department,
    visit_type="OPD", payment_type="Cash", date_of_birth=None,
    blood_group=None, emergency_contact=None, emergency_phone=None, address=None):
    
    doc = frappe.get_doc({
        "doctype": "Patient Registration",
        "full_name": full_name,
        "phone": phone,
        "gender": gender,
        "chief_complaint": chief_complaint,
        "referred_department": referred_department,
        "visit_type": visit_type,
        "payment_type": payment_type,
        "date_of_birth": date_of_birth,
        "blood_group": blood_group,
        "emergency_contact": emergency_contact,
        "emergency_phone": emergency_phone,
        "address": address,
        "status": "Registered"
    })
    doc.insert(ignore_permissions=True)
    
    today_count = frappe.db.count("Appointment", {"appointment_date": frappe.utils.today()}) + 1
    
    appt = frappe.get_doc({
        "doctype": "Appointment",
        "patient_id": doc.name,
        "department": referred_department,
        "appointment_date": frappe.utils.today(),
        "token_number": today_count,
        "status": "Scheduled"
    })
    appt.insert(ignore_permissions=True)
    frappe.db.commit()
    
    return {
        "patient_id": doc.name,
        "token_number": today_count,
        "appointment_id": appt.name,
        "full_name": full_name
    }

@frappe.whitelist()
def get_today_queue():
    return frappe.get_all("Appointment",
        filters={"appointment_date": frappe.utils.today()},
        fields=["name", "patient_id", "patient_name", "department", "token_number", "status"],
        order_by="token_number asc",
        limit=50
    )

@frappe.whitelist()
def get_today_stats():
    today = frappe.utils.today()
    today_start = today + " 00:00:00"
    return {
        "registered": frappe.db.count("Patient Registration",
            filters=[["registration_date", ">=", today_start]]),
        "waiting": frappe.db.count("Appointment",
            filters={"appointment_date": today, "status": "Scheduled"}),
        "completed": frappe.db.count("Appointment",
            filters={"appointment_date": today, "status": "Completed"})
    }
