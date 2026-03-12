import frappe

def get_patient_journey(patient_id):
    return frappe.get_all("Patient Registration", filters={"name": patient_id}, fields=["*"])

def get_department_stats():
    return {}

def get_bed_occupancy():
    return {}
