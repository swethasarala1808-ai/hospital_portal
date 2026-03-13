"""
🏥 Medicare Hospital Portal - FIXED Setup Script v2
====================================================
Fix: Detects whether your Patient Registration uses
     'patient_name' or 'full_name' automatically.

Run:
  bench --site hospital.localhost execute hospital_portal.hospital_setup_v2.run_full_setup

OR in bench console:
  exec(open('/home/swetha/frappe-bench/hospital_setup_v2.py').read())
"""

import frappe
from frappe.utils import now_datetime, today, nowtime
import random

# ─────────────────────────────────────────────
# AUTO-DETECT FIELD NAMES
# ─────────────────────────────────────────────

def get_patient_name_field():
    """Detect whether doctype uses 'patient_name' or 'full_name'"""
    try:
        meta = frappe.get_meta("Patient Registration")
        field_names = [f.fieldname for f in meta.fields]
        if "patient_name" in field_names:
            return "patient_name"
        elif "full_name" in field_names:
            return "full_name"
        elif "name1" in field_names:
            return "name1"
        else:
            # Print all fields to help debug
            print(f"  ⚠️  Available fields in Patient Registration: {field_names[:20]}")
            return "full_name"  # fallback
    except Exception as e:
        print(f"  ⚠️  Could not read Patient Registration meta: {e}")
        return "full_name"

def get_doctype_fields(doctype_name):
    """Get all fieldnames for a doctype"""
    try:
        meta = frappe.get_meta(doctype_name)
        return [f.fieldname for f in meta.fields]
    except:
        return []

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────

DEPARTMENT_USERS = [
    {"email": "registration@medicare.com", "first_name": "Priya",    "last_name": "Sharma",  "role": "Registration Staff", "department": "Registration", "username": "reg_staff",         "password": "Medicare@2026"},
    {"email": "nurse@medicare.com",        "first_name": "Anitha",   "last_name": "Rajan",   "role": "Nurse",              "department": "Nursing",      "username": "nurse_anitha",      "password": "Medicare@2026"},
    {"email": "doctor@medicare.com",       "first_name": "Suresh",   "last_name": "Kumar",   "role": "Doctor",             "department": "OPD",          "username": "dr_suresh",         "password": "Medicare@2026"},
    {"email": "lab@medicare.com",          "first_name": "Karthik",  "last_name": "Nair",    "role": "Lab Technician",     "department": "Laboratory",   "username": "lab_karthik",       "password": "Medicare@2026"},
    {"email": "radiology@medicare.com",    "first_name": "Deepa",    "last_name": "Menon",   "role": "Radiographer",       "department": "Radiology",    "username": "rad_deepa",         "password": "Medicare@2026"},
    {"email": "pharmacy@medicare.com",     "first_name": "Venkat",   "last_name": "Rao",     "role": "Pharmacist",         "department": "Pharmacy",     "username": "pharmacist_venkat", "password": "Medicare@2026"},
    {"email": "ward@medicare.com",         "first_name": "Lakshmi",  "last_name": "Devi",    "role": "Ward Nurse",         "department": "IPD",          "username": "ward_lakshmi",      "password": "Medicare@2026"},
    {"email": "icu@medicare.com",          "first_name": "Ramesh",   "last_name": "Babu",    "role": "ICU Nurse",          "department": "ICU",          "username": "icu_ramesh",        "password": "Medicare@2026"},
]

PATIENTS = [
    {"name": "Arun Krishnamurthy", "age": 45, "gender": "Male",   "phone": "9876543210", "blood": "B+",  "complaint": "Chest pain and breathlessness"},
    {"name": "Meena Sundaram",     "age": 32, "gender": "Female", "phone": "9876543211", "blood": "O+",  "complaint": "Fever and body ache for 3 days"},
    {"name": "Vijay Anand",        "age": 58, "gender": "Male",   "phone": "9876543212", "blood": "A+",  "complaint": "Diabetic review, high sugar levels"},
    {"name": "Kavitha Rajan",      "age": 27, "gender": "Female", "phone": "9876543213", "blood": "AB+", "complaint": "Abdominal pain"},
    {"name": "Subramaniam T",      "age": 70, "gender": "Male",   "phone": "9876543214", "blood": "O-",  "complaint": "Knee pain, difficulty walking"},
    {"name": "Preethi Shankar",    "age": 38, "gender": "Female", "phone": "9876543215", "blood": "B-",  "complaint": "Headache and dizziness"},
    {"name": "Balu Natarajan",     "age": 52, "gender": "Male",   "phone": "9876543216", "blood": "A-",  "complaint": "Hypertension follow-up"},
    {"name": "Saranya Murugan",    "age": 24, "gender": "Female", "phone": "9876543217", "blood": "O+",  "complaint": "Skin allergy"},
    {"name": "Gopalakrishnan R",   "age": 65, "gender": "Male",   "phone": "9876543218", "blood": "B+",  "complaint": "Shortness of breath, admitted"},
    {"name": "Divya Lakshmi",      "age": 30, "gender": "Female", "phone": "9876543219", "blood": "A+",  "complaint": "Post surgery monitoring - ICU"},
]

def log(msg):  print(f"  ✅ {msg}")
def warn(msg): print(f"  ⚠️  {msg}")


# ─────────────────────────────────────────────
# STEP 1: Roles
# ─────────────────────────────────────────────

def create_roles():
    print("\n📋 Creating Roles...")
    for role_name in ["Registration Staff","Nurse","Doctor","Lab Technician","Pathologist",
                      "Radiographer","Radiologist","Pharmacist","Ward Nurse","ICU Nurse",
                      "Intensivist","Hospital Head"]:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(ignore_permissions=True)
            log(f"Role created: {role_name}")
        else:
            log(f"Role exists: {role_name}")


# ─────────────────────────────────────────────
# STEP 2: Users
# ─────────────────────────────────────────────

def create_users():
    print("\n👥 Creating Department Users...")
    for u in DEPARTMENT_USERS:
        if frappe.db.exists("User", u["email"]):
            user_doc = frappe.get_doc("User", u["email"])
            warn(f"User exists: {u['email']}")
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

        existing_roles = [r.role for r in user_doc.get("roles", [])]
        if u["role"] not in existing_roles:
            user_doc.append("roles", {"role": u["role"]})
            user_doc.save(ignore_permissions=True)
            log(f"  → Role '{u['role']}' assigned")


# ─────────────────────────────────────────────
# STEP 3: Patients + Appointments
# ─────────────────────────────────────────────

def create_patients_and_appointments():
    print("\n📋 Creating Patient Registrations & Appointments...")

    # Auto-detect the name field
    name_field = get_patient_name_field()
    print(f"  ℹ️  Using field '{name_field}' for patient name")

    # Get all available fields
    pat_fields = get_doctype_fields("Patient Registration")
    appt_fields = get_doctype_fields("Appointment")
    print(f"  ℹ️  Patient Registration fields: {pat_fields[:15]}")

    patient_ids = []
    appointment_ids = []

    doctors = ["Dr. Suresh Kumar", "Dr. Priya Arun", "Dr. Ramesh Babu", "Dr. Meena Pillai"]
    specialties = ["General Medicine", "Cardiology", "Orthopedics", "Dermatology"]

    for i, p in enumerate(PATIENTS):
        # Build patient doc with only fields that exist
        pat_data = {
            "doctype": "Patient Registration",
            name_field: p["name"],
        }

        # Add optional fields only if they exist in the doctype
        optional_fields = {
            "age": p["age"],
            "gender": p["gender"],
            "phone": p["phone"],
            "mobile": p["phone"],
            "mobile_no": p["phone"],
            "blood_group": p["blood"],
            "chief_complaint": p["complaint"],
            "complaint": p["complaint"],
            "registration_date": today(),
            "date": today(),
            "status": "Registered",
            "address": f"{random.randint(1,200)}, Anna Nagar, Chennai",
        }
        for field, value in optional_fields.items():
            if field in pat_fields:
                pat_data[field] = value

        # Check duplicate
        existing = frappe.db.get_value("Patient Registration", {name_field: p["name"]}, "name")
        if existing:
            patient_id = existing
            log(f"Patient exists: {p['name']} → {patient_id}")
        else:
            try:
                pat = frappe.get_doc(pat_data)
                pat.insert(ignore_permissions=True)
                patient_id = pat.name
                log(f"Patient: {p['name']} → {patient_id}")
            except Exception as e:
                warn(f"Patient {p['name']} failed: {e}")
                # Try minimal insert
                try:
                    pat = frappe.get_doc({"doctype": "Patient Registration", name_field: p["name"]})
                    pat.insert(ignore_permissions=True)
                    patient_id = pat.name
                    log(f"Patient (minimal): {p['name']} → {patient_id}")
                except Exception as e2:
                    warn(f"Patient minimal also failed: {e2}")
                    continue

        patient_ids.append(patient_id)

        # Appointment / Token
        appt_data = {
            "doctype": "Appointment",
            "patient": patient_id,
            "token_number": i + 1,
            "status": "Scheduled",
        }

        # Add optional appointment fields
        appt_optional = {
            "patient_name": p["name"],
            "full_name": p["name"],
            "appointment_date": today(),
            "date": today(),
            "appointment_time": f"{9 + i}:00:00",
            "time": f"{9 + i}:00:00",
            "doctor": doctors[i % 4],
            "department": specialties[i % 4],
            "consultation_fee": 500,
            "fee": 500,
        }
        for field, value in appt_optional.items():
            if field in appt_fields:
                appt_data[field] = value

        existing_appt = frappe.db.get_value("Appointment", {"patient": patient_id}, "name")
        if existing_appt:
            appointment_ids.append(existing_appt)
            log(f"  Token exists for {p['name']}")
        else:
            try:
                appt = frappe.get_doc(appt_data)
                appt.insert(ignore_permissions=True)
                appointment_ids.append(appt.name)
                log(f"  Token #{i+1} → {appt.name}")
            except Exception as e:
                warn(f"  Appointment for {p['name']} failed: {e}")
                appointment_ids.append(None)

    return patient_ids, appointment_ids


# ─────────────────────────────────────────────
# STEP 4: Vital Signs
# ─────────────────────────────────────────────

def create_vital_signs(patient_ids):
    print("\n🩺 Creating Vital Signs...")
    fields = get_doctype_fields("Vital Signs")
    print(f"  ℹ️  Vital Signs fields: {fields[:20]}")

    vitals = [
        (120,80,37.2,98,70,168,72,"Green"),
        (138,90,38.5,96,88,155,60,"Yellow"),
        (145,95,37.8,95,92,175,85,"Orange"),
        (110,70,36.8,99,72,162,55,"Green"),
        (160,100,37.5,94,78,170,80,"Orange"),
        (125,82,37.1,97,76,158,62,"Green"),
        (150,98,37.9,93,88,172,90,"Yellow"),
        (118,76,36.9,98,74,163,57,"Green"),
    ]

    for i, pid in enumerate(patient_ids[:8]):
        if frappe.db.exists("Vital Signs", {"patient": pid}):
            log(f"Vitals exist: {PATIENTS[i]['name']}")
            continue
        d = vitals[i]
        doc = {"doctype": "Vital Signs", "patient": pid}
        optional = {
            "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
            "date": today(), "recording_date": today(), "time": nowtime(),
            "bp_systolic": d[0], "systolic": d[0],
            "bp_diastolic": d[1], "diastolic": d[1],
            "temperature": d[2], "body_temperature": d[2],
            "spo2": d[3], "oxygen_saturation": d[3],
            "pulse": d[4], "pulse_rate": d[4], "heart_rate": d[4],
            "height": d[5], "weight": d[6],
            "triage_level": d[7], "triage": d[7],
        }
        for f, v in optional.items():
            if f in fields: doc[f] = v
        try:
            frappe.get_doc(doc).insert(ignore_permissions=True)
            log(f"Vitals: {PATIENTS[i]['name']} BP {d[0]}/{d[1]} SpO2 {d[3]}% [{d[7]}]")
        except Exception as e:
            warn(f"Vitals {PATIENTS[i]['name']}: {e}")


# ─────────────────────────────────────────────
# STEP 5: Consultations + Prescriptions
# ─────────────────────────────────────────────

def create_consultations(patient_ids, appointment_ids):
    print("\n👨‍⚕️ Creating Consultations & Prescriptions...")
    cons_fields = get_doctype_fields("Consultation")
    rx_fields   = get_doctype_fields("Prescription")

    data = [
        {"diag": "Hypertensive Heart Disease",         "notes": "Chest pain, ECG changes. Start amlodipine.",              "meds": [("Amlodipine","5mg","OD",30),("Aspirin","75mg","OD",30)]},
        {"diag": "Viral Fever - Dengue Suspected",     "notes": "Fever 38.5C x 3 days. Dengue NS1 ordered.",              "meds": [("Paracetamol","500mg","TID",5),("ORS","1 sachet","TID",5)]},
        {"diag": "Type 2 Diabetes - Uncontrolled",     "notes": "FBS 280. HbA1c ordered. Increase Metformin.",             "meds": [("Metformin","1000mg","BD",30),("Glipizide","5mg","OD",30)]},
        {"diag": "Acute Appendicitis (suspected)",     "notes": "RIF pain, USG ordered. Surgical consult.",                "meds": [("Inj. Buscopan","20mg","IM stat",1)]},
        {"diag": "Osteoarthritis Knee Bilateral",      "notes": "Grade 3 OA. Physio + NSAID.",                             "meds": [("Diclofenac","50mg","BD",15),("Calcium D3","500mg","OD",30)]},
        {"diag": "Tension Headache + Hypertension",    "notes": "BP 125/82. Lifestyle advice.",                            "meds": [("Paracetamol","650mg","SOS",10),("Telmisartan","40mg","OD",30)]},
        {"diag": "Essential Hypertension",             "notes": "BP 150/98. Continue medications.",                        "meds": [("Amlodipine","10mg","OD",30),("Losartan","50mg","OD",30)]},
        {"diag": "Allergic Dermatitis",                "notes": "Pruritic rash. Antihistamine + steroid cream.",           "meds": [("Cetirizine","10mg","OD",10),("Betamethasone Cream","0.1%","BD",1)]},
    ]

    cons_ids = []
    rx_ids   = []

    for i, pid in enumerate(patient_ids[:8]):
        d = data[i]
        appt_id = appointment_ids[i] if i < len(appointment_ids) else None

        # Consultation
        existing = frappe.db.get_value("Consultation", {"patient": pid}, "name")
        if existing:
            cons_ids.append(existing)
            log(f"Consultation exists: {PATIENTS[i]['name']}")
        else:
            doc = {"doctype": "Consultation", "patient": pid}
            opts = {
                "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
                "appointment": appt_id, "consultation_date": today(), "date": today(),
                "doctor": "Dr. Suresh Kumar", "physician": "Dr. Suresh Kumar",
                "diagnosis": d["diag"], "primary_diagnosis": d["diag"],
                "clinical_notes": d["notes"], "notes": d["notes"], "complaints": d["notes"],
                "status": "Completed",
            }
            for f, v in opts.items():
                if f in cons_fields and v is not None: doc[f] = v
            try:
                cons = frappe.get_doc(doc)
                cons.insert(ignore_permissions=True)
                cons_ids.append(cons.name)
                log(f"Consultation: {PATIENTS[i]['name']} → {d['diag']}")
            except Exception as e:
                warn(f"Consultation {PATIENTS[i]['name']}: {e}")
                cons_ids.append(None)
                rx_ids.append(None)
                continue

        # Prescription
        existing_rx = frappe.db.get_value("Prescription", {"patient": pid}, "name")
        if existing_rx:
            rx_ids.append(existing_rx)
            log(f"  Prescription exists: {PATIENTS[i]['name']}")
        else:
            doc = {"doctype": "Prescription", "patient": pid}
            opts = {
                "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
                "consultation": cons_ids[-1], "prescription_date": today(), "date": today(),
                "doctor": "Dr. Suresh Kumar", "status": "Active",
            }
            for f, v in opts.items():
                if f in rx_fields and v is not None: doc[f] = v

            # Find the medicines child table field name
            meta = frappe.get_meta("Prescription")
            child_fields = [f for f in meta.fields if f.fieldtype == "Table"]
            medicine_field = child_fields[0].fieldname if child_fields else "medicines"

            try:
                rx = frappe.get_doc(doc)
                for med in d["meds"]:
                    row = {"medicine_name": med[0], "drug_name": med[0], "item": med[0],
                           "dosage": med[1], "dose": med[1],
                           "frequency": med[2], "period": f"{med[3]} days",
                           "duration": med[3], "duration_days": med[3]}
                    # Only add fields that exist in child doctype
                    rx.append(medicine_field, {k: v for k, v in row.items()})
                rx.insert(ignore_permissions=True)
                rx_ids.append(rx.name)
                log(f"  Prescription: {len(d['meds'])} medicines → {rx.name}")
            except Exception as e:
                warn(f"  Prescription {PATIENTS[i]['name']}: {e}")
                rx_ids.append(None)

    return cons_ids, rx_ids


# ─────────────────────────────────────────────
# STEP 6: Lab Requests + Reports
# ─────────────────────────────────────────────

def create_lab_data(patient_ids, cons_ids):
    print("\n🔬 Creating Lab Requests & Reports...")
    lr_fields  = get_doctype_fields("Lab Request")
    lrp_fields = get_doctype_fields("Lab Report")

    lab_data = [
        {"tests": "ECG, Cardiac Enzymes, Lipid Profile", "results": "Troponin I: 0.8 ng/mL (elevated), LDL: 160 mg/dL", "conclusion": "Elevated cardiac enzymes. Cardiology review.", "urgent": True},
        {"tests": "CBC, Dengue NS1 Antigen, Dengue IgM", "results": "Platelet: 85000 (low), Dengue NS1: POSITIVE",       "conclusion": "Dengue fever confirmed. Monitor platelets.",  "urgent": True},
        {"tests": "HbA1c, FBS, PPBS, KFT",               "results": "HbA1c: 9.2%, FBS: 280 mg/dL",                      "conclusion": "Poorly controlled diabetes.",                 "urgent": False},
        {"tests": "CBC, CRP, Urine Routine",              "results": "WBC: 14000 (elevated), CRP: 48 mg/L",              "conclusion": "Raised inflammatory markers.",                "urgent": True},
        {"tests": "Uric Acid, RA Factor, CRP",            "results": "Uric Acid: 7.2 mg/dL, RA Factor: Negative",        "conclusion": "Mild hyperuricemia. OA confirmed.",           "urgent": False},
    ]

    for i in range(min(5, len(patient_ids))):
        pid = patient_ids[i]
        ld = lab_data[i]
        cons_id = cons_ids[i] if i < len(cons_ids) else None

        existing = frappe.db.get_value("Lab Request", {"patient": pid}, "name")
        if not existing:
            doc = {"doctype": "Lab Request", "patient": pid}
            opts = {
                "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
                "consultation": cons_id, "requested_date": today(), "date": today(),
                "requested_by": "Dr. Suresh Kumar", "doctor": "Dr. Suresh Kumar",
                "tests_requested": ld["tests"], "tests": ld["tests"],
                "urgent": 1 if ld["urgent"] else 0, "status": "Completed",
            }
            for f, v in opts.items():
                if f in lr_fields and v is not None: doc[f] = v
            try:
                lr = frappe.get_doc(doc)
                lr.insert(ignore_permissions=True)
                existing = lr.name
                log(f"Lab Request: {PATIENTS[i]['name']} → {ld['tests'][:40]}")
            except Exception as e:
                warn(f"Lab Request {PATIENTS[i]['name']}: {e}")
                continue

        if not frappe.db.exists("Lab Report", {"patient": pid}):
            doc = {"doctype": "Lab Report", "patient": pid}
            opts = {
                "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
                "lab_request": existing, "report_date": today(), "date": today(),
                "technician": "Karthik Nair", "lab_technician": "Karthik Nair",
                "test_results": ld["results"], "results": ld["results"],
                "clinical_conclusion": ld["conclusion"], "conclusion": ld["conclusion"],
                "status": "Verified",
            }
            for f, v in opts.items():
                if f in lrp_fields and v is not None: doc[f] = v
            try:
                frappe.get_doc(doc).insert(ignore_permissions=True)
                log(f"  Lab Report: {ld['conclusion'][:50]}")
            except Exception as e:
                warn(f"  Lab Report {PATIENTS[i]['name']}: {e}")


# ─────────────────────────────────────────────
# STEP 7: Radiology
# ─────────────────────────────────────────────

def create_radiology_data(patient_ids, cons_ids):
    print("\n📡 Creating Radiology Requests & Reports...")
    rr_fields  = get_doctype_fields("Radiology Request")
    rrp_fields = get_doctype_fields("Radiology Report")

    radio_data = [
        {"scan": "Chest X-Ray + Echo",           "findings": "Cardiomegaly, EF 45%",                           "impression": "Dilated cardiomyopathy. Cardiology consult."},
        {"scan": "USG Abdomen and Pelvis",        "findings": "Appendix 9mm, periappendiceal stranding",        "impression": "Acute appendicitis. Surgical review advised."},
        {"scan": "X-Ray Knee AP/Lateral bilateral","findings": "Joint space narrowing, osteophytes",            "impression": "Grade 3 OA bilateral knees."},
    ]
    indices = [0, 3, 4]

    for j, i in enumerate(indices):
        if i >= len(patient_ids): continue
        pid = patient_ids[i]
        rd = radio_data[j]
        cons_id = cons_ids[i] if i < len(cons_ids) else None

        existing = frappe.db.get_value("Radiology Request", {"patient": pid}, "name")
        if not existing:
            doc = {"doctype": "Radiology Request", "patient": pid}
            opts = {
                "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
                "consultation": cons_id, "requested_date": today(), "date": today(),
                "requested_by": "Dr. Suresh Kumar",
                "scan_type": rd["scan"], "examination": rd["scan"],
                "clinical_indication": PATIENTS[i]["complaint"], "status": "Completed",
            }
            for f, v in opts.items():
                if f in rr_fields and v is not None: doc[f] = v
            try:
                rr = frappe.get_doc(doc)
                rr.insert(ignore_permissions=True)
                existing = rr.name
                log(f"Radiology Request: {PATIENTS[i]['name']} → {rd['scan']}")
            except Exception as e:
                warn(f"Radiology Request {PATIENTS[i]['name']}: {e}")
                continue

        if not frappe.db.exists("Radiology Report", {"patient": pid}):
            doc = {"doctype": "Radiology Report", "patient": pid}
            opts = {
                "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
                "radiology_request": existing, "report_date": today(), "date": today(),
                "radiographer": "Deepa Menon",
                "findings": rd["findings"], "report": rd["findings"],
                "impression": rd["impression"], "status": "Verified",
            }
            for f, v in opts.items():
                if f in rrp_fields and v is not None: doc[f] = v
            try:
                frappe.get_doc(doc).insert(ignore_permissions=True)
                log(f"  Radiology Report: {rd['impression'][:50]}")
            except Exception as e:
                warn(f"  Radiology Report {PATIENTS[i]['name']}: {e}")


# ─────────────────────────────────────────────
# STEP 8: Pharmacy
# ─────────────────────────────────────────────

def create_pharmacy_data(patient_ids, rx_ids):
    print("\n💊 Creating Pharmacy Dispensing...")
    fields = get_doctype_fields("Pharmacy Dispensing")

    for i in range(min(6, len(patient_ids))):
        pid = patient_ids[i]
        rx_id = rx_ids[i] if i < len(rx_ids) else None
        if frappe.db.exists("Pharmacy Dispensing", {"patient": pid}):
            log(f"Pharmacy exists: {PATIENTS[i]['name']}")
            continue
        doc = {"doctype": "Pharmacy Dispensing", "patient": pid}
        opts = {
            "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
            "prescription": rx_id, "dispense_date": today(), "date": today(),
            "pharmacist": "Venkat Rao",
            "status": "Dispensed",
            "total_amount": random.choice([150, 280, 420, 560, 175, 340]),
            "amount": random.choice([150, 280, 420, 560]),
        }
        for f, v in opts.items():
            if f in fields and v is not None: doc[f] = v
        try:
            frappe.get_doc(doc).insert(ignore_permissions=True)
            log(f"Pharmacy: {PATIENTS[i]['name']} → dispensed ✓")
        except Exception as e:
            warn(f"Pharmacy {PATIENTS[i]['name']}: {e}")


# ─────────────────────────────────────────────
# STEP 9: IPD Admissions
# ─────────────────────────────────────────────

def create_ipd_data(patient_ids):
    print("\n🛏️ Creating IPD Admissions...")
    fields = get_doctype_fields("IPD Admission")

    ipd_list = [
        {"idx": 8, "diag": "COPD Exacerbation",          "ward": "General Ward A", "bed": "WARD-A-01", "doctor": "Dr. Suresh Kumar"},
        {"idx": 3, "diag": "Post-op Appendectomy Day 1",  "ward": "Surgical Ward",  "bed": "WARD-C-01", "doctor": "Dr. Ramesh Babu"},
    ]
    for ipd in ipd_list:
        i = ipd["idx"]
        pid = patient_ids[i]
        if frappe.db.exists("IPD Admission", {"patient": pid}):
            log(f"IPD exists: {PATIENTS[i]['name']}")
            continue
        doc = {"doctype": "IPD Admission", "patient": pid}
        opts = {
            "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
            "admission_date": today(), "date": today(), "admission_time": nowtime(),
            "admitting_doctor": ipd["doctor"], "doctor": ipd["doctor"],
            "ward": ipd["ward"], "bed_number": ipd["bed"], "bed": ipd["bed"],
            "diagnosis_at_admission": ipd["diag"], "diagnosis": ipd["diag"],
            "status": "Admitted",
        }
        for f, v in opts.items():
            if f in fields and v is not None: doc[f] = v
        try:
            frappe.get_doc(doc).insert(ignore_permissions=True)
            log(f"IPD: {PATIENTS[i]['name']} → {ipd['ward']} Bed {ipd['bed']}")
        except Exception as e:
            warn(f"IPD {PATIENTS[i]['name']}: {e}")


# ─────────────────────────────────────────────
# STEP 10: ICU
# ─────────────────────────────────────────────

def create_icu_data(patient_ids):
    print("\n🚨 Creating ICU Monitoring...")
    fields = get_doctype_fields("ICU Monitoring")

    i = 9  # Divya Lakshmi
    pid = patient_ids[i]

    readings = [
        (96, 120, 80, 88, 37.2, "Stable",   "Nasal O2 2L/min"),
        (95, 118, 78, 90, 37.4, "Stable",   "Nasal O2 2L/min"),
        (93, 125, 85, 94, 37.8, "Guarded",  "Nasal O2 4L/min"),
    ]
    for j, r in enumerate(readings):
        doc = {"doctype": "ICU Monitoring", "patient": pid}
        opts = {
            "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
            "monitoring_date": today(), "date": today(),
            "monitoring_time": f"0{8+j*2}:00:00", "time": f"0{8+j*2}:00:00",
            "spo2": r[0], "oxygen_saturation": r[0],
            "bp_systolic": r[1], "systolic": r[1],
            "bp_diastolic": r[2], "diastolic": r[2],
            "pulse": r[3], "heart_rate": r[3],
            "temperature": r[4],
            "condition": r[5], "patient_condition": r[5],
            "ventilator_support": r[6], "support": r[6],
            "nurse": "Ramesh Babu", "nurse_name": "Ramesh Babu",
        }
        for f, v in opts.items():
            if f in fields and v is not None: doc[f] = v
        try:
            frappe.get_doc(doc).insert(ignore_permissions=True)
            log(f"ICU [{j+1}]: {PATIENTS[i]['name']} SpO2 {r[0]}% BP {r[1]}/{r[2]} [{r[5]}]")
        except Exception as e:
            warn(f"ICU reading {j+1}: {e}")


# ─────────────────────────────────────────────
# STEP 11: Nursing Tasks
# ─────────────────────────────────────────────

def create_nursing_tasks(patient_ids):
    print("\n👩‍⚕️ Creating Nursing Tasks...")
    fields = get_doctype_fields("Nursing Task")

    tasks = [
        (0, "Injection",    "Injection Pantoprazole 40mg IV",             "Done"),
        (1, "IV Fluid",     "IV Normal Saline 500ml over 4 hours",        "In Progress"),
        (2, "Monitoring",   "Blood sugar check every 6 hours",            "Pending"),
        (3, "Wound Care",   "Daily dressing of surgical wound",           "Done"),
        (8, "Nebulization", "Duolin nebulization 4th hourly",             "In Progress"),
        (9, "Catheter Care","Foley catheter care + urine output charting","Pending"),
    ]
    for task in tasks:
        i, task_type, desc, status = task
        if i >= len(patient_ids): continue
        pid = patient_ids[i]
        if frappe.db.exists("Nursing Task", {"patient": pid}):
            continue
        doc = {"doctype": "Nursing Task", "patient": pid}
        opts = {
            "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
            "task_date": today(), "date": today(),
            "task_type": task_type, "type": task_type,
            "task_description": desc, "description": desc, "task": desc,
            "status": status,
            "assigned_nurse": "Anitha Rajan", "nurse": "Anitha Rajan",
        }
        for f, v in opts.items():
            if f in fields and v is not None: doc[f] = v
        try:
            frappe.get_doc(doc).insert(ignore_permissions=True)
            log(f"Nursing Task: {PATIENTS[i]['name']} → {desc[:40]} [{status}]")
        except Exception as e:
            warn(f"Nursing Task {PATIENTS[i]['name']}: {e}")


# ─────────────────────────────────────────────
# MASTER RUN
# ─────────────────────────────────────────────

def run_full_setup():
    print("\n" + "=" * 65)
    print("  🏥 MEDICARE HOSPITAL - SETUP v2 (field-adaptive)")
    print("=" * 65)

    try: create_roles()
    except Exception as e: warn(f"Roles: {e}")

    try: create_users()
    except Exception as e: warn(f"Users: {e}")

    try:
        patient_ids, appointment_ids = create_patients_and_appointments()
    except Exception as e:
        warn(f"Patients: {e}")
        return

    if not patient_ids:
        warn("No patients created — stopping.")
        return

    try: create_vital_signs(patient_ids)
    except Exception as e: warn(f"Vitals: {e}")

    cons_ids, rx_ids = [], []
    try: cons_ids, rx_ids = create_consultations(patient_ids, appointment_ids)
    except Exception as e: warn(f"Consultations: {e}")

    try: create_lab_data(patient_ids, cons_ids)
    except Exception as e: warn(f"Lab: {e}")

    try: create_radiology_data(patient_ids, cons_ids)
    except Exception as e: warn(f"Radiology: {e}")

    try: create_pharmacy_data(patient_ids, rx_ids)
    except Exception as e: warn(f"Pharmacy: {e}")

    try: create_ipd_data(patient_ids)
    except Exception as e: warn(f"IPD: {e}")

    try: create_icu_data(patient_ids)
    except Exception as e: warn(f"ICU: {e}")

    try: create_nursing_tasks(patient_ids)
    except Exception as e: warn(f"Nursing: {e}")

    frappe.db.commit()

    print("\n" + "=" * 65)
    print("  ✅ SETUP COMPLETE!")
    print("=" * 65)
    print("""
  🔐 LOGIN CREDENTIALS (all passwords: Medicare@2026)
  ─────────────────────────────────────────────────────
  registration@medicare.com  →  /registration-portal
  nurse@medicare.com         →  /nurse-portal
  doctor@medicare.com        →  /doctor-portal
  lab@medicare.com           →  /lab-portal
  radiology@medicare.com     →  /radiology-portal
  pharmacy@medicare.com      →  /pharmacy-portal
  ward@medicare.com          →  /ipd-portal
  icu@medicare.com           →  /icu-portal
  ─────────────────────────────────────────────────────
  Admin: admin123@gmail.com  →  /hospital-dashboard
  ─────────────────────────────────────────────────────
""")
