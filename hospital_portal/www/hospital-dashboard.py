import frappe

no_cache = 1

def get_context(context):
    return context

@frappe.whitelist(allow_guest=False)
def get_live_stats():
    today = frappe.utils.today()
    today_start = today + " 00:00:00"

    def safe_count(sql, *args):
        try:
            return frappe.db.sql(sql, args, as_list=True)[0][0]
        except:
            return 0

    opd = safe_count(
        "SELECT COUNT(*) FROM `tabPatient Registration` WHERE creation >= %s",
        today_start)

    beds = safe_count(
        "SELECT COUNT(*) FROM `tabIPD Admission` WHERE status = %s",
        "Admitted")

    lab = safe_count(
        "SELECT COUNT(*) FROM `tabLab Request` WHERE status IN ('Requested','Sample Collected','In Process')")

    radio = safe_count(
        "SELECT COUNT(*) FROM `tabRadiology Request` WHERE status IN ('Requested','Scheduled','In Progress')")

    consult = safe_count(
        "SELECT COUNT(*) FROM `tabConsultation` WHERE creation >= %s",
        today_start)

    rx = safe_count(
        "SELECT COUNT(*) FROM `tabPrescription` WHERE creation >= %s",
        today_start)

    icu = safe_count(
        "SELECT COUNT(*) FROM `tabICU Monitoring` WHERE creation >= %s",
        today_start)

    return {
        "opd_today": opd,
        "beds_occupied": beds,
        "pending_lab": lab,
        "pending_radiology": radio,
        "consultations_today": consult,
        "prescriptions_today": rx,
        "icu_patients": icu,
        "pending_orders": lab + radio,
        "total_patients": frappe.db.count("Patient Registration")
    }
