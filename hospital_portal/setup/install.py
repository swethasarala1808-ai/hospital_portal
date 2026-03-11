import frappe
from frappe import _


HOSPITAL_ROLES = [
    {"role_name": "Hospital Head",      "desk_access": 1},
    {"role_name": "Registration Staff", "desk_access": 1},
    {"role_name": "Nurse",              "desk_access": 1},
    {"role_name": "Doctor",             "desk_access": 1},
    {"role_name": "Lab Technician",     "desk_access": 1},
    {"role_name": "Pathologist",        "desk_access": 1},
    {"role_name": "Radiographer",       "desk_access": 1},
    {"role_name": "Radiologist",        "desk_access": 1},
    {"role_name": "Pharmacist",         "desk_access": 1},
    {"role_name": "Ward Nurse",         "desk_access": 1},
    {"role_name": "ICU Nurse",          "desk_access": 1},
    {"role_name": "Intensivist",        "desk_access": 1},
]

SAMPLE_DEPARTMENTS = [
    "Registration",
    "Nursing / Triage",
    "Consultation / OPD",
    "Laboratory",
    "Radiology",
    "Pharmacy",
    "IPD / Ward",
    "ICU",
    "Emergency",
    "Administration",
]

SAMPLE_BED_TYPES = [
    {"bed_type": "General",       "ward": "General Ward",    "count": 20},
    {"bed_type": "Semi-Private",  "ward": "Semi-Private",    "count": 10},
    {"bed_type": "Private",       "ward": "Private Ward",    "count": 5},
    {"bed_type": "ICU",           "ward": "ICU",             "count": 6},
    {"bed_type": "Isolation",     "ward": "Isolation Ward",  "count": 2},
]


def after_install():
    print("🏥 Setting up Hospital Portal...")
    create_roles()
    create_sample_beds()
    create_hospital_settings()
    print("✅ Hospital Portal setup complete!")


def after_migrate():
    create_roles()


def before_uninstall():
    print("⚠️  Removing Hospital Portal roles...")


def create_roles():
    for role_data in HOSPITAL_ROLES:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.get_doc({
                "doctype": "Role",
                "role_name": role_data["role_name"],
                "desk_access": role_data.get("desk_access", 1),
            })
            role.insert(ignore_permissions=True)
            print(f"  ✅ Role created: {role_data['role_name']}")
        else:
            print(f"  ⏭️  Role exists: {role_data['role_name']}")
    frappe.db.commit()


def create_sample_beds():
    """Create initial bed records if none exist."""
    if frappe.db.count("Bed Management") > 0:
        return

    bed_num = 1
    for bed_config in SAMPLE_BED_TYPES:
        for i in range(bed_config["count"]):
            bed_id = f"BED-{bed_config['ward'][:3].upper()}-{str(bed_num).zfill(3)}"
            if not frappe.db.exists("Bed Management", bed_id):
                bed = frappe.get_doc({
                    "doctype": "Bed Management",
                    "bed_id": bed_id,
                    "ward_name": bed_config["ward"],
                    "bed_type": bed_config["bed_type"],
                    "is_occupied": 0,
                })
                bed.insert(ignore_permissions=True)
            bed_num += 1

    frappe.db.commit()
    print(f"  ✅ {bed_num-1} beds created")


def create_hospital_settings():
    """Create Hospital Settings document if not exists."""
    if not frappe.db.exists("Hospital Settings", "Hospital Settings"):
        doc = frappe.get_doc({
            "doctype": "Hospital Settings",
            "hospital_name": "My Hospital",
            "clinic_mode": "Hospital",
            "token_prefix": "T",
            "patient_id_prefix": "PAT",
            "appointment_id_prefix": "APT",
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("  ✅ Hospital Settings created")
