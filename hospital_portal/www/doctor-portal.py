import frappe
from frappe import _

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login"), frappe.PermissionError)
    return context

@frappe.whitelist()
def get_doctor_queue():
    today_start = frappe.utils.today() + " 00:00:00"
    return frappe.db.sql("""
        SELECT name, full_name, phone, referred_department,
               visit_type, triage_status, token_number,
               chief_complaint, blood_group, gender, date_of_birth
        FROM `tabPatient Registration`
        WHERE creation >= %s
        AND triage_status IN ('Waiting', 'Vitals Recorded', 'With Doctor')
        AND referred_department = 'Consultation / OPD'
        ORDER BY token_number ASC
    """, today_start, as_dict=True)

@frappe.whitelist()
def get_patient_details(patient_id):
    pat = frappe.get_doc("Patient Registration", patient_id)
    
    vitals = frappe.db.sql("""
        SELECT * FROM `tabVital Signs`
        WHERE patient_id = %s
        ORDER BY creation DESC LIMIT 1
    """, patient_id, as_dict=True)
    
    consultations = frappe.get_all("Consultation",
        filters={"patient_id": patient_id},
        fields=["name","diagnosis","treatment_plan","consultation_date","status"],
        order_by="creation desc", limit=5)

    lab_reports = frappe.get_all("Lab Request",
        filters={"patient_id": patient_id},
        fields=["name","test_names","status","results"],
        order_by="creation desc", limit=5)

    radiology = frappe.get_all("Radiology Request",
        filters={"patient_id": patient_id},
        fields=["name","modality","status","findings"],
        order_by="creation desc", limit=5)

    return {
        "patient": pat.as_dict(),
        "vitals": vitals[0] if vitals else None,
        "consultations": consultations,
        "lab_reports": lab_reports,
        "radiology": radiology
    }

@frappe.whitelist()
def save_consultation(patient_id, chief_complaint, examination_findings,
    diagnosis, treatment_plan, order_lab=0, order_radiology=0,
    order_prescription=0, order_nursing=0, admit_patient=0,
    follow_up_date=None):

    doc = frappe.get_doc({
        "doctype": "Consultation",
        "patient_id": patient_id,
        "doctor": frappe.session.user,
        "consultation_date": frappe.utils.now(),
        "chief_complaint": chief_complaint,
        "examination_findings": examination_findings,
        "diagnosis": diagnosis,
        "treatment_plan": treatment_plan,
        "order_lab": int(order_lab),
        "order_radiology": int(order_radiology),
        "order_prescription": int(order_prescription),
        "order_nursing": int(order_nursing),
        "admit_patient": int(admit_patient),
        "follow_up_date": follow_up_date or None,
        "status": "Completed"
    })
    doc.insert(ignore_permissions=True)

    # Update patient status
    new_status = "Admitted" if int(admit_patient) else "In Lab" if int(order_lab) else "In Radiology" if int(order_radiology) else "In Pharmacy" if int(order_prescription) else "Discharged"
    frappe.db.set_value("Patient Registration", patient_id, "triage_status", new_status)
    frappe.db.commit()

    return {"consultation_id": doc.name, "new_status": new_status}
