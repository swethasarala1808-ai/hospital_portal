import frappe

no_cache = 1

def get_context(context):
    return context

@frappe.whitelist()
def get_live_stats():
    today_start = frappe.utils.today() + " 00:00:00"

    def sc(sql, *args):
        try:
            return frappe.db.sql(sql, args)[0][0] or 0
        except:
            return 0

    opd      = sc("SELECT COUNT(*) FROM `tabPatient Registration` WHERE creation >= %s", today_start)
    waiting  = sc("SELECT COUNT(*) FROM `tabPatient Registration` WHERE creation >= %s AND status='Registered'", today_start)
    vitals   = sc("SELECT COUNT(*) FROM `tabVital Signs` WHERE creation >= %s", today_start)
    consult  = sc("SELECT COUNT(*) FROM `tabConsultation` WHERE creation >= %s", today_start)
    lab      = sc("SELECT COUNT(*) FROM `tabLab Request` WHERE status IN ('Requested','Sample Collected','In Process')")
    radio    = sc("SELECT COUNT(*) FROM `tabRadiology Request` WHERE status IN ('Requested','Scheduled','In Progress')")
    rx       = sc("SELECT COUNT(*) FROM `tabPrescription` WHERE creation >= %s", today_start)
    ipd      = sc("SELECT COUNT(*) FROM `tabIPD Admission` WHERE status = 'Admitted'")
    icu      = sc("SELECT COUNT(*) FROM `tabICU Monitoring` WHERE creation >= %s", today_start)
    total    = sc("SELECT COUNT(*) FROM `tabPatient Registration`")

    return {
        "opd_today": opd,
        "waiting": waiting,
        "vitals_today": vitals,
        "consultations_today": consult,
        "pending_lab": lab,
        "pending_radiology": radio,
        "prescriptions_today": rx,
        "beds_occupied": ipd,
        "icu_patients": icu,
        "pending_orders": lab + radio,
        "total_patients": total
    }
