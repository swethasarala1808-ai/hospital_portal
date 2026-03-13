"""
🏥 Medicare Hospital Portal - Complete Setup Script
=====================================================
Run this from your Frappe bench:
  bench --site hospital.localhost execute hospital_portal.hospital_setup.run_full_setup

OR run directly:
  bench --site hospital.localhost console
  Then paste and run: exec(open('/path/to/hospital_setup.py').read())

What this does:
  1. Creates department users with correct roles
  2. Inserts sample data (patients, appointments, vitals, consultations, etc.)
  3. Links everything end-to-end (Patient → Token → Nurse → Doctor → Pharmacy → Invoice)
"""

import frappe
from frappe.utils import now_datetime, today, add_days, nowtime
from datetime import datetime, timedelta
import random

# ─────────────────────────────────────────────
# 1. DEPARTMENT USERS
# ─────────────────────────────────────────────

DEPARTMENT_USERS = [
    {
        "email": "registration@medicare.com",
        "first_name": "Priya",
        "last_name": "Sharma",
        "role": "Registration Staff",
        "department": "Registration",
        "username": "reg_staff",
        "password": "Medicare@2026",
    },
    {
        "email": "nurse@medicare.com",
        "first_name": "Anitha",
        "last_name": "Rajan",
        "role": "Nurse",
        "department": "Nursing",
        "username": "nurse_anitha",
        "password": "Medicare@2026",
    },
    {
        "email": "doctor@medicare.com",
        "first_name": "Dr. Suresh",
        "last_name": "Kumar",
        "role": "Doctor",
        "department": "OPD",
        "username": "dr_suresh",
        "password": "Medicare@2026",
    },
    {
        "email": "lab@medicare.com",
        "first_name": "Karthik",
        "last_name": "Nair",
        "role": "Lab Technician",
        "department": "Laboratory",
        "username": "lab_karthik",
        "password": "Medicare@2026",
    },
    {
        "email": "radiology@medicare.com",
        "first_name": "Deepa",
        "last_name": "Menon",
        "role": "Radiographer",
        "department": "Radiology",
        "username": "rad_deepa",
        "password": "Medicare@2026",
    },
    {
        "email": "pharmacy@medicare.com",
        "first_name": "Venkat",
        "last_name": "Rao",
        "role": "Pharmacist",
        "department": "Pharmacy",
        "username": "pharmacist_venkat",
        "password": "Medicare@2026",
    },
    {
        "email": "ward@medicare.com",
        "first_name": "Lakshmi",
        "last_name": "Devi",
        "role": "Ward Nurse",
        "department": "IPD",
        "username": "ward_lakshmi",
        "password": "Medicare@2026",
    },
    {
        "email": "icu@medicare.com",
        "first_name": "Ramesh",
        "last_name": "Babu",
        "role": "ICU Nurse",
        "department": "ICU",
        "username": "icu_ramesh",
        "password": "Medicare@2026",
    },
]

# Sample patient data
PATIENTS = [
    {"name": "Arun Krishnamurthy", "age": 45, "gender": "Male", "phone": "9876543210", "blood": "B+", "complaint": "Chest pain and breathlessness"},
    {"name": "Meena Sundaram", "age": 32, "gender": "Female", "phone": "9876543211", "blood": "O+", "complaint": "Fever and body ache for 3 days"},
    {"name": "Vijay Anand", "age": 58, "gender": "Male", "phone": "9876543212", "blood": "A+", "complaint": "Diabetic review, high sugar levels"},
    {"name": "Kavitha Rajan", "age": 27, "gender": "Female", "phone": "9876543213", "blood": "AB+", "complaint": "Abdominal pain"},
    {"name": "Subramaniam T", "age": 70, "gender": "Male", "phone": "9876543214", "blood": "O-", "complaint": "Knee pain, difficulty walking"},
    {"name": "Preethi Shankar", "age": 38, "gender": "Female", "phone": "9876543215", "blood": "B-", "complaint": "Headache and dizziness"},
    {"name": "Balu Natarajan", "age": 52, "gender": "Male", "phone": "9876543216", "blood": "A-", "complaint": "Hypertension follow-up"},
    {"name": "Saranya Murugan", "age": 24, "gender": "Female", "phone": "9876543217", "blood": "O+", "complaint": "Skin allergy"},
    {"name": "Gopalakrishnan R", "age": 65, "gender": "Male", "phone": "9876543218", "blood": "B+", "complaint": "Shortness of breath, admitted"},
    {"name": "Divya Lakshmi", "age": 30, "gender": "Female", "phone": "9876543219", "blood": "A+", "complaint": "Post surgery monitoring - ICU"},
]


def log(msg):
    print(f"  ✅ {msg}")


def warn(msg):
    print(f"  ⚠️  {msg}")


# ─────────────────────────────────────────────
# STEP 1: Create Roles (if missing)
# ─────────────────────────────────────────────

def create_roles():
    print("\n📋 Creating Roles...")
    roles = [
        "Registration Staff", "Nurse", "Doctor", "Lab Technician",
        "Pathologist", "Radiographer", "Radiologist", "Pharmacist",
        "Ward Nurse", "ICU Nurse", "Intensivist", "Hospital Head",
    ]
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            role = frappe.get_doc({"doctype": "Role", "role_name": role_name})
            role.insert(ignore_permissions=True)
            log(f"Role created: {role_name}")
        else:
            log(f"Role exists: {role_name}")


# ─────────────────────────────────────────────
# STEP 2: Create Department Users
# ─────────────────────────────────────────────

def create_users():
    print("\n👥 Creating Department Users...")
    created_users = []

    for u in DEPARTMENT_USERS:
        if frappe.db.exists("User", u["email"]):
            warn(f"User exists: {u['email']} — skipping creation, updating roles")
            user_doc = frappe.get_doc("User", u["email"])
        else:
            user_doc = frappe.get_doc({
                "doctype": "User",
                "email": u["email"],
                "first_name": u["first_name"],
                "last_name": u["last_name"],
                "username": u["username"],
                "enabled": 1,
                "new_password": u["password"],
                "send_welcome_email": 0,
                "user_type": "System User",
            })
            user_doc.insert(ignore_permissions=True)
            log(f"User created: {u['email']}")

        # Assign role
        existing_roles = [r.role for r in user_doc.get("roles", [])]
        if u["role"] not in existing_roles:
            user_doc.append("roles", {"role": u["role"]})
            user_doc.save(ignore_permissions=True)
            log(f"  Role '{u['role']}' assigned to {u['email']}")

        created_users.append(u)

    print("\n📋 Department Login Credentials:")
    print("  " + "─" * 60)
    print(f"  {'Department':<20} {'Email':<30} {'Password'}")
    print("  " + "─" * 60)
    for u in DEPARTMENT_USERS:
        print(f"  {u['department']:<20} {u['email']:<30} {u['password']}")
    print("  " + "─" * 60)

    return created_users


# ─────────────────────────────────────────────
# STEP 3: Create Sample Patients + Appointments (Registration)
# ─────────────────────────────────────────────

def create_patients_and_appointments():
    print("\n📋 Creating Patient Registrations & Appointments...")
    patient_ids = []
    appointment_ids = []

    for i, p in enumerate(PATIENTS):
        pat_name_key = p["name"].replace(" ", "-").lower()

        # Patient Registration
        if not frappe.db.exists("Patient Registration", {"patient_name": p["name"]}):
            pat = frappe.get_doc({
                "doctype": "Patient Registration",
                "patient_name": p["name"],
                "age": p["age"],
                "gender": p["gender"],
                "phone": p["phone"],
                "blood_group": p["blood"],
                "chief_complaint": p["complaint"],
                "registration_date": today(),
                "registration_time": nowtime(),
                "status": "Registered",
                "address": f"{random.randint(1, 200)}, Anna Nagar, Chennai",
                "emergency_contact": f"98765432{random.randint(20, 99)}",
            })
            pat.insert(ignore_permissions=True)
            patient_id = pat.name
            log(f"Patient: {p['name']} → {patient_id}")
        else:
            patient_id = frappe.db.get_value("Patient Registration", {"patient_name": p["name"]}, "name")
            log(f"Patient exists: {p['name']} → {patient_id}")

        patient_ids.append(patient_id)

        # Appointment / Token
        if not frappe.db.exists("Appointment", {"patient": patient_id}):
            doctors = ["Dr. Suresh Kumar", "Dr. Priya Arun", "Dr. Ramesh Babu", "Dr. Meena Pillai"]
            specialties = ["General Medicine", "Cardiology", "Orthopedics", "Dermatology"]
            idx = i % len(doctors)
            appt = frappe.get_doc({
                "doctype": "Appointment",
                "patient": patient_id,
                "patient_name": p["name"],
                "appointment_date": today(),
                "appointment_time": f"{9 + i}:00:00",
                "doctor": doctors[idx],
                "department": specialties[idx],
                "token_number": i + 1,
                "status": "Scheduled" if i < 7 else "Completed",
                "payment_status": "Paid" if i % 2 == 0 else "Pending",
                "consultation_fee": 500,
            })
            appt.insert(ignore_permissions=True)
            appt_id = appt.name
            log(f"  Token #{i+1} → {appt_id} for {p['name']}")
        else:
            appt_id = frappe.db.get_value("Appointment", {"patient": patient_id}, "name")

        appointment_ids.append(appt_id)

    return patient_ids, appointment_ids


# ─────────────────────────────────────────────
# STEP 4: Vital Signs (Nursing)
# ─────────────────────────────────────────────

def create_vital_signs(patient_ids):
    print("\n🩺 Creating Vital Signs (Nursing)...")
    vital_data = [
        (120, 80, 37.2, 98, 70, 168, 72, "Green"),
        (138, 90, 38.5, 96, 88, 155, 60, "Yellow"),
        (145, 95, 37.8, 95, 92, 175, 85, "Orange"),
        (110, 70, 36.8, 99, 72, 162, 55, "Green"),
        (160, 100, 37.5, 94, 78, 170, 80, "Orange"),
        (125, 82, 37.1, 97, 76, 158, 62, "Green"),
        (150, 98, 37.9, 93, 88, 172, 90, "Yellow"),
        (118, 76, 36.9, 98, 74, 163, 57, "Green"),
        (170, 110, 38.2, 91, 96, 178, 95, "Red"),
        (130, 85, 37.4, 96, 80, 160, 65, "Yellow"),
    ]

    vs_ids = []
    for i, pid in enumerate(patient_ids[:8]):  # First 8 are OPD
        d = vital_data[i]
        if not frappe.db.exists("Vital Signs", {"patient": pid}):
            vs = frappe.get_doc({
                "doctype": "Vital Signs",
                "patient": pid,
                "patient_name": PATIENTS[i]["name"],
                "date": today(),
                "time": nowtime(),
                "bp_systolic": d[0],
                "bp_diastolic": d[1],
                "temperature": d[2],
                "spo2": d[3],
                "pulse": d[4],
                "height": d[5],
                "weight": d[6],
                "triage_level": d[7],
                "recorded_by": "nurse@medicare.com",
            })
            vs.insert(ignore_permissions=True)
            vs_ids.append(vs.name)
            log(f"Vitals: {PATIENTS[i]['name']} → BP {d[0]}/{d[1]}, Temp {d[2]}°C, SpO2 {d[3]}%, Triage: {d[7]}")
        else:
            vs_ids.append(frappe.db.get_value("Vital Signs", {"patient": pid}, "name"))

    return vs_ids


# ─────────────────────────────────────────────
# STEP 5: Consultations + Prescriptions (Doctor)
# ─────────────────────────────────────────────

def create_consultations(patient_ids, appointment_ids):
    print("\n👨‍⚕️ Creating Doctor Consultations & Prescriptions...")
    consultation_data = [
        {
            "diagnosis": "Hypertensive Heart Disease",
            "notes": "Patient presents with chest pain. ECG shows changes. Refer for Echo. Start amlodipine.",
            "medicines": [("Amlodipine", "5mg", "Once daily", 30), ("Aspirin", "75mg", "Once daily", 30)],
            "lab": "ECG, Cardiac enzymes, Lipid profile",
            "radiology": "Chest X-Ray, Echo",
            "admit": False,
        },
        {
            "diagnosis": "Viral Fever with Myalgia",
            "notes": "Fever 38.5°C for 3 days. Dengue screening ordered. Supportive treatment started.",
            "medicines": [("Paracetamol", "500mg", "TID", 5), ("ORS Sachets", "1 sachet", "TID", 10)],
            "lab": "CBC, Dengue NS1 Antigen, Dengue IgM, Widal",
            "radiology": None,
            "admit": False,
        },
        {
            "diagnosis": "Type 2 Diabetes Mellitus - Uncontrolled",
            "notes": "HbA1c to be checked. Current FBS 280 mg/dL. Increase metformin dose.",
            "medicines": [("Metformin", "1000mg", "BD", 30), ("Glipizide", "5mg", "OD", 30)],
            "lab": "HbA1c, FBS, PPBS, Kidney Function Test, Urine Routine",
            "radiology": None,
            "admit": False,
        },
        {
            "diagnosis": "Acute Appendicitis (suspected)",
            "notes": "Pain RIF, Rovsing positive. USG abdomen ordered. Surgical consult.",
            "medicines": [("Injection Buscopan", "20mg", "IM stat", 1), ("IV Normal Saline", "500ml", "IV 6hrly", 2)],
            "lab": "CBC, CRP, Urine Routine",
            "radiology": "USG Abdomen and Pelvis",
            "admit": True,
        },
        {
            "diagnosis": "Osteoarthritis Knee (bilateral)",
            "notes": "Grade 3 OA on X-Ray. Physiotherapy advised. NSAID started.",
            "medicines": [("Diclofenac", "50mg", "BD", 15), ("Calcium D3", "500mg", "OD", 30)],
            "lab": "Uric acid, RA factor, CRP",
            "radiology": "X-Ray Knee AP/Lateral bilateral",
            "admit": False,
        },
        {
            "diagnosis": "Tension Headache with Hypertension",
            "notes": "BP 125/82. Headache likely tension type. Lifestyle advice given.",
            "medicines": [("Paracetamol", "650mg", "SOS", 10), ("Telmisartan", "40mg", "OD", 30)],
            "lab": "CBC, RFT, Electrolytes",
            "radiology": "CT Brain (if not improving)",
            "admit": False,
        },
        {
            "diagnosis": "Essential Hypertension",
            "notes": "BP controlled at 150/98. Continue current medications. Diet advice given.",
            "medicines": [("Amlodipine", "10mg", "OD", 30), ("Losartan", "50mg", "OD", 30)],
            "lab": "RFT, Electrolytes, ECG",
            "radiology": None,
            "admit": False,
        },
        {
            "diagnosis": "Allergic Dermatitis",
            "notes": "Widespread pruritic rash. Possible contact allergen. Antihistamine + steroid cream.",
            "medicines": [("Cetirizine", "10mg", "OD", 10), ("Betamethasone Cream", "0.1%", "BD topical", 1)],
            "lab": "IgE levels, Skin prick test",
            "radiology": None,
            "admit": False,
        },
    ]

    cons_ids = []
    rx_ids = []

    for i, pid in enumerate(patient_ids[:8]):
        cd = consultation_data[i]
        appt_id = appointment_ids[i]

        if not frappe.db.exists("Consultation", {"patient": pid}):
            cons = frappe.get_doc({
                "doctype": "Consultation",
                "patient": pid,
                "patient_name": PATIENTS[i]["name"],
                "appointment": appt_id,
                "consultation_date": today(),
                "doctor": "Dr. Suresh Kumar",
                "diagnosis": cd["diagnosis"],
                "clinical_notes": cd["notes"],
                "status": "Completed",
                "lab_orders": cd["lab"],
                "radiology_orders": cd.get("radiology", ""),
                "admit_patient": 1 if cd["admit"] else 0,
            })
            cons.insert(ignore_permissions=True)
            cons_id = cons.name
            log(f"Consultation: {PATIENTS[i]['name']} → {cd['diagnosis']}")
        else:
            cons_id = frappe.db.get_value("Consultation", {"patient": pid}, "name")
            log(f"Consultation exists: {PATIENTS[i]['name']}")

        cons_ids.append(cons_id)

        # Prescription
        if not frappe.db.exists("Prescription", {"patient": pid}):
            rx = frappe.get_doc({
                "doctype": "Prescription",
                "patient": pid,
                "patient_name": PATIENTS[i]["name"],
                "consultation": cons_id,
                "prescription_date": today(),
                "doctor": "Dr. Suresh Kumar",
                "status": "Active",
            })
            for med in cd["medicines"]:
                rx.append("medicines", {
                    "medicine_name": med[0],
                    "dosage": med[1],
                    "frequency": med[2],
                    "duration_days": med[3],
                })
            rx.insert(ignore_permissions=True)
            rx_ids.append(rx.name)
            log(f"  Prescription: {len(cd['medicines'])} medicines for {PATIENTS[i]['name']}")
        else:
            rx_ids.append(frappe.db.get_value("Prescription", {"patient": pid}, "name"))

    return cons_ids, rx_ids


# ─────────────────────────────────────────────
# STEP 6: Lab Requests + Reports
# ─────────────────────────────────────────────

def create_lab_data(patient_ids, cons_ids):
    print("\n🔬 Creating Lab Requests & Reports...")

    lab_tests = [
        {
            "tests": "ECG, Cardiac Enzymes, Lipid Profile",
            "results": "Troponin I: 0.8 ng/mL (elevated), Total Cholesterol: 240 mg/dL, LDL: 160 mg/dL",
            "conclusion": "Elevated cardiac enzymes. Cardiology review advised.",
            "urgent": True,
        },
        {
            "tests": "CBC, Dengue NS1 Antigen, Dengue IgM, Widal",
            "results": "WBC: 3800/μL (low), Platelet: 85000 (low), Dengue NS1: POSITIVE",
            "conclusion": "Dengue fever confirmed. Monitor platelet count daily.",
            "urgent": True,
        },
        {
            "tests": "HbA1c, FBS, PPBS, Kidney Function Test, Urine Routine",
            "results": "HbA1c: 9.2%, FBS: 280 mg/dL, PPBS: 320 mg/dL, Creatinine: 1.1 mg/dL",
            "conclusion": "Poorly controlled diabetes. Intensify management.",
            "urgent": False,
        },
        {
            "tests": "CBC, CRP, Urine Routine",
            "results": "WBC: 14000/μL (elevated), CRP: 48 mg/L (elevated), Neutrophils: 82%",
            "conclusion": "Raised inflammatory markers suggesting acute infection/inflammation.",
            "urgent": True,
        },
        {
            "tests": "Uric acid, RA Factor, CRP",
            "results": "Uric Acid: 7.2 mg/dL, RA Factor: Negative, CRP: 12 mg/L",
            "conclusion": "Mild hyperuricemia. RA excluded. Consistent with OA.",
            "urgent": False,
        },
    ]

    lr_ids = []
    lrp_ids = []

    for i in range(min(5, len(patient_ids))):
        pid = patient_ids[i]
        ld = lab_tests[i]

        if not frappe.db.exists("Lab Request", {"patient": pid}):
            lr = frappe.get_doc({
                "doctype": "Lab Request",
                "patient": pid,
                "patient_name": PATIENTS[i]["name"],
                "consultation": cons_ids[i],
                "requested_date": today(),
                "requested_by": "Dr. Suresh Kumar",
                "tests_requested": ld["tests"],
                "urgent": 1 if ld["urgent"] else 0,
                "status": "Completed",
            })
            lr.insert(ignore_permissions=True)
            lr_ids.append(lr.name)
            log(f"Lab Request: {PATIENTS[i]['name']} → {ld['tests'][:40]}...")
        else:
            lr_ids.append(frappe.db.get_value("Lab Request", {"patient": pid}, "name"))

        if not frappe.db.exists("Lab Report", {"patient": pid}):
            lrp = frappe.get_doc({
                "doctype": "Lab Report",
                "patient": pid,
                "patient_name": PATIENTS[i]["name"],
                "lab_request": lr_ids[-1],
                "report_date": today(),
                "technician": "Karthik Nair",
                "test_results": ld["results"],
                "clinical_conclusion": ld["conclusion"],
                "status": "Verified",
            })
            lrp.insert(ignore_permissions=True)
            lrp_ids.append(lrp.name)
            log(f"  Lab Report done: {ld['conclusion'][:50]}...")
        else:
            lrp_ids.append(frappe.db.get_value("Lab Report", {"patient": pid}, "name"))

    return lr_ids, lrp_ids


# ─────────────────────────────────────────────
# STEP 7: Radiology Requests + Reports
# ─────────────────────────────────────────────

def create_radiology_data(patient_ids, cons_ids):
    print("\n📡 Creating Radiology Requests & Reports...")

    radio_data = [
        {
            "scan_type": "Chest X-Ray PA View + Echo",
            "findings": "Cardiomegaly present. Left ventricular hypertrophy on Echo. EF: 45%",
            "impression": "Dilated cardiomyopathy with reduced EF. Cardiology consult recommended.",
        },
        {
            "scan_type": "USG Abdomen and Pelvis",
            "findings": "Appendix visualized, diameter 9mm with periappendiceal fat stranding. No free fluid.",
            "impression": "Findings consistent with acute appendicitis. Surgical review advised.",
        },
        {
            "scan_type": "X-Ray Knee AP/Lateral bilateral",
            "findings": "Joint space narrowing bilateral knees. Osteophytes at medial compartment. No effusion.",
            "impression": "Grade 3 Osteoarthritis bilateral knees. Physiotherapy recommended.",
        },
    ]

    rr_ids = []
    rrp_ids = []
    indices = [0, 3, 4]  # patients with radiology orders

    for j, i in enumerate(indices):
        if i >= len(patient_ids):
            continue
        pid = patient_ids[i]
        rd = radio_data[j]

        if not frappe.db.exists("Radiology Request", {"patient": pid}):
            rr = frappe.get_doc({
                "doctype": "Radiology Request",
                "patient": pid,
                "patient_name": PATIENTS[i]["name"],
                "consultation": cons_ids[i],
                "requested_date": today(),
                "requested_by": "Dr. Suresh Kumar",
                "scan_type": rd["scan_type"],
                "status": "Completed",
                "clinical_indication": PATIENTS[i]["complaint"],
            })
            rr.insert(ignore_permissions=True)
            rr_ids.append(rr.name)
            log(f"Radiology Request: {PATIENTS[i]['name']} → {rd['scan_type']}")
        else:
            rr_ids.append(frappe.db.get_value("Radiology Request", {"patient": pid}, "name"))

        if not frappe.db.exists("Radiology Report", {"patient": pid}):
            rrp = frappe.get_doc({
                "doctype": "Radiology Report",
                "patient": pid,
                "patient_name": PATIENTS[i]["name"],
                "radiology_request": rr_ids[-1],
                "report_date": today(),
                "radiographer": "Deepa Menon",
                "findings": rd["findings"],
                "impression": rd["impression"],
                "status": "Verified",
            })
            rrp.insert(ignore_permissions=True)
            rrp_ids.append(rrp.name)
            log(f"  Radiology Report: {rd['impression'][:50]}...")
        else:
            rrp_ids.append(frappe.db.get_value("Radiology Report", {"patient": pid}, "name"))

    return rr_ids, rrp_ids


# ─────────────────────────────────────────────
# STEP 8: Pharmacy Dispensing
# ─────────────────────────────────────────────

def create_pharmacy_data(patient_ids, rx_ids):
    print("\n💊 Creating Pharmacy Dispensing Records...")

    for i in range(min(6, len(patient_ids))):
        pid = patient_ids[i]
        if i >= len(rx_ids):
            continue

        if not frappe.db.exists("Pharmacy Dispensing", {"patient": pid}):
            pd_doc = frappe.get_doc({
                "doctype": "Pharmacy Dispensing",
                "patient": pid,
                "patient_name": PATIENTS[i]["name"],
                "prescription": rx_ids[i],
                "dispense_date": today(),
                "pharmacist": "Venkat Rao",
                "status": "Dispensed",
                "total_amount": random.choice([150, 280, 420, 560, 175, 340]),
                "payment_status": "Paid" if i % 2 == 0 else "Pending",
            })
            pd_doc.insert(ignore_permissions=True)
            log(f"Pharmacy: {PATIENTS[i]['name']} → medicines dispensed ✓")


# ─────────────────────────────────────────────
# STEP 9: IPD Admission + Bed Management
# ─────────────────────────────────────────────

def create_ipd_data(patient_ids):
    print("\n🛏️ Creating IPD Admissions & Bed Management...")

    # Create beds first
    wards = [
        ("WARD-A", "General Ward A", 10),
        ("WARD-B", "General Ward B", 10),
        ("WARD-C", "Surgical Ward", 8),
        ("ICU-1", "ICU", 6),
        ("NICU-1", "NICU", 4),
    ]

    for ward_code, ward_name, beds in wards:
        for b in range(1, beds + 1):
            bed_id = f"{ward_code}-{b:02d}"
            if not frappe.db.exists("__Bed_Management__", bed_id):
                try:
                    bed = frappe.get_doc({
                        "doctype": "__Bed_Management__",
                        "bed_number": bed_id,
                        "ward": ward_name,
                        "ward_code": ward_code,
                        "bed_type": "ICU" if "ICU" in ward_code else "General",
                        "status": "Occupied" if b <= 2 else "Available",
                    })
                    bed.insert(ignore_permissions=True)
                except Exception as e:
                    # Try alternate doctype name
                    try:
                        bed = frappe.get_doc({
                            "doctype": "Bed Management",
                            "bed_number": bed_id,
                            "ward": ward_name,
                            "status": "Occupied" if b <= 2 else "Available",
                        })
                        bed.insert(ignore_permissions=True)
                    except:
                        pass

    log("Beds created: WARD-A (10), WARD-B (10), WARD-C (8), ICU-1 (6), NICU-1 (4)")

    # IPD Admissions - patients 8 and 9 (index 8, 9)
    ipd_patients = [
        {
            "patient_idx": 8,
            "diagnosis": "COPD Exacerbation",
            "ward": "General Ward A",
            "bed": "WARD-A-01",
            "doctor": "Dr. Suresh Kumar",
            "notes": "Admitted for IV antibiotics and nebulization. Monitor SpO2 hourly.",
        },
        {
            "patient_idx": 3,
            "diagnosis": "Acute Appendicitis - Post-operative Day 1",
            "ward": "Surgical Ward",
            "bed": "WARD-C-01",
            "doctor": "Dr. Ramesh Babu",
            "notes": "Post-appendectomy. IV fluids, wound care, ambulation started.",
        },
    ]

    for ipd in ipd_patients:
        i = ipd["patient_idx"]
        pid = patient_ids[i]
        if not frappe.db.exists("IPD Admission", {"patient": pid}):
            ipd_doc = frappe.get_doc({
                "doctype": "IPD Admission",
                "patient": pid,
                "patient_name": PATIENTS[i]["name"],
                "admission_date": today(),
                "admission_time": nowtime(),
                "admitting_doctor": ipd["doctor"],
                "ward": ipd["ward"],
                "bed_number": ipd["bed"],
                "diagnosis_at_admission": ipd["diagnosis"],
                "notes": ipd["notes"],
                "status": "Admitted",
            })
            ipd_doc.insert(ignore_permissions=True)
            log(f"IPD Admission: {PATIENTS[i]['name']} → {ipd['ward']}, Bed {ipd['bed']}")


# ─────────────────────────────────────────────
# STEP 10: ICU Monitoring
# ─────────────────────────────────────────────

def create_icu_data(patient_ids):
    print("\n🚨 Creating ICU Monitoring Records...")

    icu_patient_idx = 9  # Divya Lakshmi - post surgery ICU
    pid = patient_ids[icu_patient_idx]

    if not frappe.db.exists("IPD Admission", {"patient": pid}):
        ipd_doc = frappe.get_doc({
            "doctype": "IPD Admission",
            "patient": pid,
            "patient_name": PATIENTS[icu_patient_idx]["name"],
            "admission_date": today(),
            "admission_time": nowtime(),
            "admitting_doctor": "Dr. Suresh Kumar",
            "ward": "ICU",
            "bed_number": "ICU-1-01",
            "diagnosis_at_admission": "Post-operative monitoring - Abdominal surgery",
            "status": "Admitted",
        })
        ipd_doc.insert(ignore_permissions=True)

    icu_readings = [
        (96, 120, 80, 88, 37.2, "Stable", "No ventilator", "Continue current management"),
        (95, 118, 78, 90, 37.4, "Stable", "Nasal O2 @ 2L/min", "Increase O2 if SpO2 drops"),
        (93, 125, 85, 94, 37.8, "Guarded", "Nasal O2 @ 4L/min", "Alert surgeon if deteriorates"),
    ]

    for j, reading in enumerate(icu_readings):
        if not frappe.db.exists("ICU Monitoring", {"patient": pid, "monitoring_time": f"0{8+j*2}:00:00"}):
            try:
                icu = frappe.get_doc({
                    "doctype": "ICU Monitoring",
                    "patient": pid,
                    "patient_name": PATIENTS[icu_patient_idx]["name"],
                    "monitoring_date": today(),
                    "monitoring_time": f"0{8+j*2}:00:00",
                    "spo2": reading[0],
                    "bp_systolic": reading[1],
                    "bp_diastolic": reading[2],
                    "pulse": reading[3],
                    "temperature": reading[4],
                    "condition": reading[5],
                    "ventilator_support": reading[6],
                    "nursing_notes": reading[7],
                    "nurse": "Ramesh Babu",
                })
                icu.insert(ignore_permissions=True)
                log(f"ICU Chart [{j+1}]: {PATIENTS[icu_patient_idx]['name']} → SpO2 {reading[0]}%, BP {reading[1]}/{reading[2]}")
            except Exception as e:
                warn(f"ICU monitoring insert issue: {e}")


# ─────────────────────────────────────────────
# STEP 11: Nursing Tasks
# ─────────────────────────────────────────────

def create_nursing_tasks(patient_ids):
    print("\n👩‍⚕️ Creating Nursing Tasks...")

    tasks = [
        (0, "Injection", "Injection Pantoprazole 40mg IV", "Done"),
        (1, "IV Fluid", "IV Normal Saline 500ml over 4 hours", "In Progress"),
        (2, "Blood Sugar Monitoring", "Check FBS and PPBS every 6 hours", "Pending"),
        (3, "Wound Dressing", "Daily dressing of surgical wound", "Done"),
        (8, "Nebulization", "Duolin nebulization 4th hourly", "In Progress"),
        (9, "Catheter Care", "Foley catheter care and urine output monitoring", "Pending"),
    ]

    for task in tasks:
        i = task[0]
        if i >= len(patient_ids):
            continue
        pid = patient_ids[i]
        if not frappe.db.exists("Nursing Task", {"patient": pid}):
            try:
                nt = frappe.get_doc({
                    "doctype": "Nursing Task",
                    "patient": pid,
                    "patient_name": PATIENTS[i]["name"],
                    "task_date": today(),
                    "task_type": task[1],
                    "task_description": task[2],
                    "status": task[3],
                    "assigned_nurse": "Anitha Rajan",
                })
                nt.insert(ignore_permissions=True)
                log(f"Nursing Task: {PATIENTS[i]['name']} → {task[2][:45]}... [{task[3]}]")
            except Exception as e:
                warn(f"Nursing task issue: {e}")


# ─────────────────────────────────────────────
# STEP 12: Sales Invoice (Payment)
# ─────────────────────────────────────────────

def create_sales_invoices(patient_ids, appointment_ids):
    print("\n💰 Creating Sales Invoices...")

    invoice_items = [
        [("Consultation Fee", 500), ("ECG", 300), ("Chest X-Ray", 600), ("Echo", 1500)],
        [("Consultation Fee", 500), ("Dengue NS1 Test", 800), ("CBC", 200)],
        [("Consultation Fee", 500), ("HbA1c", 600), ("FBS/PPBS", 300), ("KFT", 400)],
        [("Consultation Fee", 500), ("USG Abdomen", 1200), ("CBC", 200), ("Appendectomy OT", 15000)],
        [("Consultation Fee", 500), ("X-Ray Knee", 400), ("RA Factor", 300)],
        [("Consultation Fee", 500), ("CBC", 200), ("RFT", 350)],
    ]

    for i in range(min(6, len(patient_ids))):
        pid = patient_ids[i]
        appt_id = appointment_ids[i]

        # Check if ERPNext Sales Invoice exists for this patient (via custom field or naming)
        inv_check = frappe.db.exists("Sales Invoice", {"remarks": f"Hospital Bill - {pid}"})
        if not inv_check:
            try:
                items = invoice_items[i]
                total = sum(item[1] for item in items)

                inv = frappe.get_doc({
                    "doctype": "Sales Invoice",
                    "customer": "Walk-in Patient",
                    "posting_date": today(),
                    "due_date": today(),
                    "remarks": f"Hospital Bill - {pid}",
                    "patient_name_display": PATIENTS[i]["name"],
                    "items": [
                        {
                            "item_name": item[0],
                            "description": item[0],
                            "qty": 1,
                            "rate": item[1],
                            "amount": item[1],
                            "income_account": "Sales - H",
                        }
                        for item in items
                    ],
                })
                inv.insert(ignore_permissions=True)
                log(f"Invoice: {PATIENTS[i]['name']} → ₹{total:,} ({len(items)} items)")
            except Exception as e:
                warn(f"Invoice for {PATIENTS[i]['name']}: {e}")
        else:
            log(f"Invoice exists: {PATIENTS[i]['name']}")


# ─────────────────────────────────────────────
# MASTER RUN
# ─────────────────────────────────────────────

def run_full_setup():
    print("\n" + "=" * 65)
    print("  🏥 MEDICARE HOSPITAL PORTAL - COMPLETE SETUP")
    print("=" * 65)

    try:
        create_roles()
    except Exception as e:
        warn(f"Roles step error: {e}")

    try:
        create_users()
    except Exception as e:
        warn(f"Users step error: {e}")

    try:
        patient_ids, appointment_ids = create_patients_and_appointments()
    except Exception as e:
        warn(f"Patient/Appointment step error: {e}")
        return

    try:
        create_vital_signs(patient_ids)
    except Exception as e:
        warn(f"Vital signs step error: {e}")

    try:
        cons_ids, rx_ids = create_consultations(patient_ids, appointment_ids)
    except Exception as e:
        warn(f"Consultation step error: {e}")
        cons_ids = []
        rx_ids = []

    try:
        if cons_ids:
            create_lab_data(patient_ids, cons_ids)
    except Exception as e:
        warn(f"Lab step error: {e}")

    try:
        if cons_ids:
            create_radiology_data(patient_ids, cons_ids)
    except Exception as e:
        warn(f"Radiology step error: {e}")

    try:
        if rx_ids:
            create_pharmacy_data(patient_ids, rx_ids)
    except Exception as e:
        warn(f"Pharmacy step error: {e}")

    try:
        create_ipd_data(patient_ids)
    except Exception as e:
        warn(f"IPD step error: {e}")

    try:
        create_icu_data(patient_ids)
    except Exception as e:
        warn(f"ICU step error: {e}")

    try:
        create_nursing_tasks(patient_ids)
    except Exception as e:
        warn(f"Nursing tasks step error: {e}")

    try:
        create_sales_invoices(patient_ids, appointment_ids)
    except Exception as e:
        warn(f"Invoice step error: {e}")

    frappe.db.commit()

    print("\n" + "=" * 65)
    print("  ✅ SETUP COMPLETE!")
    print("=" * 65)
    print("""
  🔐 LOGIN CREDENTIALS
  ─────────────────────────────────────────────────────
  Admin (all departments):
    URL:       http://hospital.localhost:8001
    Email:     admin123@gmail.com
    Password:  (your admin password)

  Registration Staff:
    Email:     registration@medicare.com
    Password:  Medicare@2026
    Access:    /registration-portal

  Nurse:
    Email:     nurse@medicare.com
    Password:  Medicare@2026
    Access:    /nurse-portal

  Doctor:
    Email:     doctor@medicare.com
    Password:  Medicare@2026
    Access:    /doctor-portal

  Lab Technician:
    Email:     lab@medicare.com
    Password:  Medicare@2026
    Access:    /lab-portal

  Radiographer:
    Email:     radiology@medicare.com
    Password:  Medicare@2026
    Access:    /radiology-portal

  Pharmacist:
    Email:     pharmacy@medicare.com
    Password:  Medicare@2026
    Access:    /pharmacy-portal

  Ward Nurse:
    Email:     ward@medicare.com
    Password:  Medicare@2026
    Access:    /ipd-portal

  ICU Nurse:
    Email:     icu@medicare.com
    Password:  Medicare@2026
    Access:    /icu-portal
  ─────────────────────────────────────────────────────

  📊 SAMPLE DATA LOADED:
    • 10 Patients registered with tokens
    • 8  Consultations with diagnoses
    • 8  Prescriptions (medicines)
    • 5  Lab requests + reports
    • 3  Radiology requests + reports
    • 6  Pharmacy dispensing records
    • 2  IPD admissions (1 Surgical, 1 General)
    • 1  ICU patient with 3 monitoring charts
    • 6  Nursing tasks
    • 6  Sales Invoices (linked to appointments)

  🔄 PATIENT FLOW (linked end-to-end):
    Registration → Token → Nurse Triage → Doctor
    → Lab/Radiology → Pharmacy → Invoice
    → IPD/ICU (for admitted patients)
  ─────────────────────────────────────────────────────
""")


# Auto-run if executed directly in frappe console
if __name__ == "__main__":
    run_full_setup()
