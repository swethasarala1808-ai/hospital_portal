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

    token = frappe.db.count("Appointment") + 1

    appt = frappe.get_doc({
        "doctype": "Appointment",
        "patient_id": pat.name,
        "department": referred_department,
        "appointment_date": frappe.utils.today(),
        "token_number": token,
        "status": "Scheduled"
    })
    appt.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "patient_id": pat.name,
        "token_number": token,
        "appointment_id": appt.name,
        "full_name": full_name
    }

@frappe.whitelist()
def get_today_queue():
    today = frappe.utils.today()
    try:
        return frappe.db.sql("""
            SELECT name, patient_id, department, token_number, status
            FROM `tabAppointment`
            WHERE DATE(creation) = %s
            ORDER BY token_number ASC
            LIMIT 50
        """, today, as_dict=True)
    except Exception:
        return frappe.get_all("Appointment",
            fields=["name", "patient_id", "department", "token_number", "status"],
            limit=50,
            order_by="creation desc"
        )

@frappe.whitelist()
def get_today_stats():
    today = frappe.utils.today()
    today_start = today + " 00:00:00"

    reg = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabPatient Registration`
        WHERE creation >= %s
    """, today_start)[0][0]

    try:
        waiting = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabAppointment`
            WHERE DATE(creation) = %s AND status = 'Scheduled'
        """, today)[0][0]

        done = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabAppointment`
            WHERE DATE(creation) = %s AND status = 'Completed'
        """, today)[0][0]
    except Exception:
        waiting = 0
        done = 0

    return {
        "registered": reg,
        "waiting": waiting,
        "completed": done
    }
