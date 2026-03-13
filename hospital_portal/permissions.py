"""
🔐 Medicare Hospital - Role Permission Manager
===============================================
Run AFTER hospital_setup.py

This script sets DocType-level permissions so each department
user can ONLY see their own department's records.

Run from bench console:
  bench --site hospital.localhost console
  exec(open('/path/to/hospital_permissions.py').read())
"""

import frappe

# ─────────────────────────────────────────────
# DocType → Role mapping
# Each role can only Read/Write/Create the listed doctypes
# ─────────────────────────────────────────────

PERMISSIONS = {
    # Registration Staff: patients + appointments only
    "Registration Staff": [
        "Patient Registration",
        "Appointment",
    ],

    # Nurse: vitals + nursing tasks (can read patient/appointment)
    "Nurse": [
        "Vital Signs",
        "Nursing Task",
        "Patient Registration",   # read-only to see patient
        "Appointment",            # read-only to see token
    ],

    # Doctor: consultations + prescriptions + read all upstream
    "Doctor": [
        "Consultation",
        "Prescription",
        "Lab Request",
        "Radiology Request",
        "Patient Registration",   # read
        "Appointment",            # read
        "Vital Signs",            # read
    ],

    # Lab Technician: lab requests + reports
    "Lab Technician": [
        "Lab Request",
        "Lab Report",
        "Patient Registration",   # read
    ],

    # Radiographer: radiology requests + reports
    "Radiographer": [
        "Radiology Request",
        "Radiology Report",
        "Patient Registration",   # read
    ],

    # Pharmacist: dispensing + read prescriptions
    "Pharmacist": [
        "Pharmacy Dispensing",
        "Prescription",           # read
        "Patient Registration",   # read
    ],

    # Ward Nurse: IPD + bed management
    "Ward Nurse": [
        "IPD Admission",
        "__Bed_Management__",
        "Bed Management",
        "Nursing Task",
        "Patient Registration",   # read
    ],

    # ICU Nurse: ICU monitoring + IPD
    "ICU Nurse": [
        "ICU Monitoring",
        "IPD Admission",          # read
        "Patient Registration",   # read
        "Vital Signs",            # read
    ],

    # Hospital Head: everything (read all)
    "Hospital Head": [
        "Patient Registration", "Appointment", "Vital Signs", "Nursing Task",
        "Consultation", "Prescription", "Lab Request", "Lab Report",
        "Radiology Request", "Radiology Report", "Pharmacy Dispensing",
        "IPD Admission", "__Bed_Management__", "Bed Management", "ICU Monitoring",
    ],
}

# Which doctypes are "read-only" for a given role
READ_ONLY = {
    "Nurse": ["Patient Registration", "Appointment"],
    "Doctor": ["Patient Registration", "Appointment", "Vital Signs"],
    "Lab Technician": ["Patient Registration"],
    "Radiographer": ["Patient Registration"],
    "Pharmacist": ["Prescription", "Patient Registration"],
    "Ward Nurse": ["Patient Registration"],
    "ICU Nurse": ["IPD Admission", "Patient Registration", "Vital Signs"],
}


def set_permissions():
    print("\n🔐 Setting Role Permissions...")
    print("=" * 60)

    for role, doctypes in PERMISSIONS.items():
        print(f"\n  Role: {role}")
        read_only_list = READ_ONLY.get(role, [])

        for dt in doctypes:
            if not frappe.db.exists("DocType", dt):
                print(f"    ⚠️  DocType '{dt}' not found — skipping")
                continue

            is_read_only = dt in read_only_list
            permlevel = 0

            # Check if permission already exists
            existing = frappe.db.get_value(
                "Custom DocPerm",
                {"parent": dt, "role": role},
                "name"
            )

            if existing:
                # Update
                frappe.db.set_value("Custom DocPerm", existing, {
                    "read": 1,
                    "write": 0 if is_read_only else 1,
                    "create": 0 if is_read_only else 1,
                    "delete": 1 if role == "Hospital Head" else 0,
                    "submit": 0,
                    "cancel": 0,
                    "amend": 0,
                    "print": 1,
                    "email": 1,
                    "report": 1,
                })
                status = "read-only" if is_read_only else "read/write"
                print(f"    ✅ Updated: {dt} [{status}]")
            else:
                # Create new custom permission
                try:
                    perm = frappe.get_doc({
                        "doctype": "Custom DocPerm",
                        "parent": dt,
                        "parenttype": "DocType",
                        "parentfield": "permissions",
                        "role": role,
                        "permlevel": permlevel,
                        "read": 1,
                        "write": 0 if is_read_only else 1,
                        "create": 0 if is_read_only else 1,
                        "delete": 1 if role == "Hospital Head" else 0,
                        "submit": 0,
                        "cancel": 0,
                        "amend": 0,
                        "print": 1,
                        "email": 1,
                        "report": 1,
                    })
                    perm.insert(ignore_permissions=True)
                    status = "read-only" if is_read_only else "read/write"
                    print(f"    ✅ Set: {dt} [{status}]")
                except Exception as e:
                    print(f"    ⚠️  Could not set {dt}: {e}")

    frappe.db.commit()
    print("\n✅ All permissions configured!")
    print("""
  DEPARTMENT ACCESS MATRIX
  ─────────────────────────────────────────────────────────────
  Role              | Own Doctypes                | Patient Access
  ──────────────────|─────────────────────────────|──────────────
  Registration Staff| Patient Reg, Appointment    | Full
  Nurse             | Vital Signs, Nursing Task   | Read-only
  Doctor            | Consultation, Prescription  | Read-only
                    | Lab/Radiology Request       |
  Lab Technician    | Lab Request, Lab Report     | Read-only
  Radiographer      | Radiology Request/Report    | Read-only
  Pharmacist        | Pharmacy Dispensing         | Read-only
  Ward Nurse        | IPD Admission, Bed, Tasks   | Read-only
  ICU Nurse         | ICU Monitoring              | Read-only
  Hospital Head     | ALL (full access)           | Full
  ─────────────────────────────────────────────────────────────
""")


if __name__ == "__main__":
    set_permissions()
