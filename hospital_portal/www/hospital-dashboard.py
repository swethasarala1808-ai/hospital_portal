import frappe

def get_context(context):
    context.no_cache = 1

@frappe.whitelist()
def get_live_stats():
    today = frappe.utils.today()
    today_start = today + " 00:00:00"
    
    return {
        "opd_today": frappe.db.count("Patient Registration", 
            filters=[["registration_date", ">=", today_start]]),
        "total_patients": frappe.db.count("Patient Registration"),
        "beds_occupied": frappe.db.count("IPD Admission", 
            filters={"status": "Admitted"}),
        "pending_lab": frappe.db.count("Lab Request", 
            filters={"status": ["in", ["Requested", "Sample Collected", "In Process"]]}),
        "pending_radiology": frappe.db.count("Radiology Request", 
            filters={"status": ["in", ["Requested", "Scheduled", "In Progress"]]}),
        "icu_patients": frappe.db.count("ICU Monitoring",
            filters=[["recorded_at", ">=", today_start]]),
        "prescriptions_today": frappe.db.count("Prescription",
            filters=[["prescription_date", ">=", today_start]]),
        "consultations_today": frappe.db.count("Consultation",
            filters=[["consultation_date", ">=", today_start]]),
        "waiting": frappe.db.count("Appointment",
            filters={"appointment_date": today, "status": "Scheduled"}),
        "pending_orders": (
            frappe.db.count("Lab Request", filters={"status": "Requested"}) +
            frappe.db.count("Radiology Request", filters={"status": "Requested"})
        )
    }
