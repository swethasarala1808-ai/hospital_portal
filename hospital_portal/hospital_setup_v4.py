"""
🏥 Medicare Hospital Portal - Setup Script v4
Fix: Appointment doctype patient field auto-detection
Run: bench --site hospital.localhost execute hospital_portal.hospital_setup_v4.run_full_setup
"""

import frappe
from frappe.utils import today, nowtime
import random

PATIENTS = [
    {"name": "Arun Krishnamurthy", "age": 45, "gender": "Male",   "phone": "+91 9876543210", "blood": "B+",  "complaint": "Chest pain and breathlessness"},
    {"name": "Meena Sundaram",     "age": 32, "gender": "Female", "phone": "+91 9876543211", "blood": "O+",  "complaint": "Fever and body ache for 3 days"},
    {"name": "Vijay Anand",        "age": 58, "gender": "Male",   "phone": "+91 9876543212", "blood": "A+",  "complaint": "Diabetic review high sugar levels"},
    {"name": "Kavitha Rajan",      "age": 27, "gender": "Female", "phone": "+91 9876543213", "blood": "AB+", "complaint": "Abdominal pain"},
    {"name": "Subramaniam T",      "age": 70, "gender": "Male",   "phone": "+91 9876543214", "blood": "O-",  "complaint": "Knee pain difficulty walking"},
    {"name": "Preethi Shankar",    "age": 38, "gender": "Female", "phone": "+91 9876543215", "blood": "B-",  "complaint": "Headache and dizziness"},
    {"name": "Balu Natarajan",     "age": 52, "gender": "Male",   "phone": "+91 9876543216", "blood": "A-",  "complaint": "Hypertension follow-up"},
    {"name": "Saranya Murugan",    "age": 24, "gender": "Female", "phone": "+91 9876543217", "blood": "O+",  "complaint": "Skin allergy"},
    {"name": "Gopalakrishnan R",   "age": 65, "gender": "Male",   "phone": "+91 9876543218", "blood": "B+",  "complaint": "Shortness of breath"},
    {"name": "Divya Lakshmi",      "age": 30, "gender": "Female", "phone": "+91 9876543219", "blood": "A+",  "complaint": "Post surgery monitoring ICU"},
]

def log(msg):  print(f"  ✅ {msg}")
def warn(msg): print(f"  ⚠️  {msg}")

def get_fields(doctype):
    try:
        return [f.fieldname for f in frappe.get_meta(doctype).fields]
    except:
        return []

def get_options(doctype, fieldname):
    try:
        meta = frappe.get_meta(doctype)
        for f in meta.fields:
            if f.fieldname == fieldname and f.options:
                return [o.strip() for o in f.options.split("\n") if o.strip()]
    except:
        pass
    return []

def safe_insert(doc_dict):
    doc = frappe.get_doc(doc_dict)
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_validate = True
    doc.flags.ignore_permissions = True
    doc.insert(ignore_permissions=True)
    return doc

def find_patient_link_field(doctype):
    """Find which field in a doctype links to Patient Registration"""
    try:
        meta = frappe.get_meta(doctype)
        for f in meta.fields:
            if f.fieldtype == "Link" and f.options == "Patient Registration":
                return f.fieldname
        # fallback: look for common names
        all_fields = [f.fieldname for f in meta.fields]
        for candidate in ["patient", "patient_id", "patient_registration", "reg_id"]:
            if candidate in all_fields:
                return candidate
    except:
        pass
    return "patient"


# ─────────────────────────────────────────────
# PATIENTS
# ─────────────────────────────────────────────

def create_patients():
    print("\n📋 Creating Patient Registrations...")
    pat_fields = get_fields("Patient Registration")

    patient_ids = []
    for i, p in enumerate(PATIENTS):
        existing = frappe.db.get_value("Patient Registration", {"full_name": p["name"]}, "name")
        if existing:
            patient_ids.append(existing)
            log(f"Patient exists: {p['name']} → {existing}")
            continue

        visit_opts = get_options("Patient Registration", "visit_type")
        status_opts = get_options("Patient Registration", "status")

        doc = {
            "doctype": "Patient Registration",
            "full_name": p["name"],
            "gender": p["gender"],
            "date_of_birth": f"{2026 - p['age']}-01-01",
            "blood_group": p["blood"],
            "chief_complaint": p["complaint"],
            "registration_date": today(),
            "status": status_opts[0] if status_opts else "Registered",
        }
        if visit_opts and "visit_type" in pat_fields:
            doc["visit_type"] = visit_opts[0]
        if "phone" in pat_fields:
            doc["phone"] = p["phone"]

        try:
            pat = safe_insert(doc)
            patient_ids.append(pat.name)
            log(f"Patient: {p['name']} → {pat.name}")
        except Exception as e:
            warn(f"Patient {p['name']}: {e}")
            try:
                pat = safe_insert({"doctype": "Patient Registration", "full_name": p["name"]})
                patient_ids.append(pat.name)
                log(f"Patient (name only): {p['name']} → {pat.name}")
            except Exception as e2:
                warn(f"Patient failed completely: {e2}")

    return patient_ids


# ─────────────────────────────────────────────
# APPOINTMENTS
# ─────────────────────────────────────────────

def create_appointments(patient_ids):
    print("\n🎫 Creating Appointments / Tokens...")

    appt_fields = get_fields("Appointment")
    print(f"  ℹ️  Appointment fields: {appt_fields}")

    # Find the field that links to Patient Registration
    pat_link_field = find_patient_link_field("Appointment")
    print(f"  ℹ️  Patient link field in Appointment: '{pat_link_field}'")

    appt_status_opts = get_options("Appointment", "status")
    status_val = appt_status_opts[0] if appt_status_opts else "Scheduled"

    doctors = ["Dr. Suresh Kumar", "Dr. Priya Arun", "Dr. Ramesh Babu", "Dr. Meena Pillai"]
    specialties = ["General Medicine", "Cardiology", "Orthopedics", "Dermatology"]

    appointment_ids = []

    for i, pid in enumerate(patient_ids):
        # Search using the correct link field
        try:
            existing = frappe.db.get_value("Appointment", {pat_link_field: pid}, "name")
        except:
            existing = None

        if existing:
            appointment_ids.append(existing)
            log(f"Token exists: {PATIENTS[i]['name']}")
            continue

        doc = {"doctype": "Appointment", pat_link_field: pid}
        opts = {
            "patient_name": PATIENTS[i]["name"],
            "full_name": PATIENTS[i]["name"],
            "appointment_date": today(),
            "date": today(),
            "appointment_time": f"{(9 + i) % 24:02d}:00:00",
            "time": f"{(9 + i) % 24:02d}:00:00",
            "doctor": doctors[i % 4],
            "department": specialties[i % 4],
            "token_number": i + 1,
            "token": i + 1,
            "status": status_val,
            "consultation_fee": 500,
            "fee": 500,
        }
        for f, v in opts.items():
            if f in appt_fields:
                doc[f] = v

        try:
            appt = safe_insert(doc)
            appointment_ids.append(appt.name)
            log(f"Token #{i+1} → {appt.name} for {PATIENTS[i]['name']}")
        except Exception as e:
            warn(f"Token for {PATIENTS[i]['name']}: {e}")
            appointment_ids.append(None)

    return appointment_ids


# ─────────────────────────────────────────────
# VITAL SIGNS
# ─────────────────────────────────────────────

def create_vital_signs(patient_ids):
    print("\n🩺 Creating Vital Signs...")
    fields = get_fields("Vital Signs")
    pat_link = find_patient_link_field("Vital Signs")
    print(f"  ℹ️  Vital Signs patient field: '{pat_link}'")

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
    triage_opts = get_options("Vital Signs", "triage_level") or get_options("Vital Signs", "triage")

    for i, pid in enumerate(patient_ids[:8]):
        try:
            existing = frappe.db.get_value("Vital Signs", {pat_link: pid}, "name")
        except:
            existing = None
        if existing:
            log(f"Vitals exist: {PATIENTS[i]['name']}")
            continue

        d = vitals[i]
        triage_val = d[7]
        if triage_opts:
            triage_val = next((o for o in triage_opts if d[7].lower() in o.lower()), triage_opts[0])

        doc = {"doctype": "Vital Signs", pat_link: pid}
        opts = {
            "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
            "date": today(), "recording_date": today(), "time": nowtime(),
            "bp_systolic": d[0], "systolic": d[0],
            "bp_diastolic": d[1], "diastolic": d[1],
            "temperature": d[2], "body_temperature": d[2],
            "spo2": d[3], "oxygen_saturation": d[3],
            "pulse": d[4], "pulse_rate": d[4], "heart_rate": d[4],
            "height": d[5], "weight": d[6],
            "triage_level": triage_val, "triage": triage_val,
        }
        for f, v in opts.items():
            if f in fields: doc[f] = v
        try:
            safe_insert(doc)
            log(f"Vitals: {PATIENTS[i]['name']} BP {d[0]}/{d[1]} SpO2 {d[3]}% [{d[7]}]")
        except Exception as e:
            warn(f"Vitals {PATIENTS[i]['name']}: {e}")


# ─────────────────────────────────────────────
# CONSULTATIONS + PRESCRIPTIONS
# ─────────────────────────────────────────────

def create_consultations(patient_ids, appointment_ids):
    print("\n👨‍⚕️ Creating Consultations & Prescriptions...")
    cons_fields = get_fields("Consultation")
    rx_fields   = get_fields("Prescription")
    cons_pat_link = find_patient_link_field("Consultation")
    rx_pat_link   = find_patient_link_field("Prescription")
    print(f"  ℹ️  Consultation patient field: '{cons_pat_link}'")

    data = [
        {"diag": "Hypertensive Heart Disease",    "notes": "Chest pain ECG changes. Start amlodipine.",    "meds": [("Amlodipine","5mg","Once daily",30),("Aspirin","75mg","Once daily",30)]},
        {"diag": "Viral Fever Dengue Suspected",  "notes": "Fever 38.5C x 3 days. Dengue NS1 ordered.",   "meds": [("Paracetamol","500mg","TID",5),("ORS","1 sachet","TID",5)]},
        {"diag": "Type 2 Diabetes Uncontrolled",  "notes": "FBS 280. HbA1c ordered. Increase Metformin.", "meds": [("Metformin","1000mg","BD",30),("Glipizide","5mg","OD",30)]},
        {"diag": "Acute Appendicitis Suspected",  "notes": "RIF pain USG ordered. Surgical consult.",     "meds": [("Inj Buscopan","20mg","Stat",1)]},
        {"diag": "Osteoarthritis Knee Bilateral", "notes": "Grade 3 OA. Physio and NSAID.",               "meds": [("Diclofenac","50mg","BD",15),("Calcium D3","500mg","OD",30)]},
        {"diag": "Tension Headache Hypertension", "notes": "BP 125/82. Lifestyle advice given.",          "meds": [("Paracetamol","650mg","SOS",10),("Telmisartan","40mg","OD",30)]},
        {"diag": "Essential Hypertension",        "notes": "BP 150/98. Continue medications.",            "meds": [("Amlodipine","10mg","OD",30),("Losartan","50mg","OD",30)]},
        {"diag": "Allergic Dermatitis",           "notes": "Pruritic rash. Antihistamine started.",       "meds": [("Cetirizine","10mg","OD",10),("Betamethasone Cream","0.1%","BD",1)]},
    ]

    cons_ids, rx_ids = [], []

    for i, pid in enumerate(patient_ids[:8]):
        d = data[i]
        appt_id = appointment_ids[i] if i < len(appointment_ids) else None

        try:
            existing = frappe.db.get_value("Consultation", {cons_pat_link: pid}, "name")
        except:
            existing = None

        if existing:
            cons_ids.append(existing)
            log(f"Consultation exists: {PATIENTS[i]['name']}")
        else:
            doc = {"doctype": "Consultation", cons_pat_link: pid}
            opts = {
                "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
                "appointment": appt_id, "consultation_date": today(), "date": today(),
                "doctor": "Dr. Suresh Kumar", "physician": "Dr. Suresh Kumar",
                "diagnosis": d["diag"], "primary_diagnosis": d["diag"],
                "clinical_notes": d["notes"], "notes": d["notes"],
                "status": "Completed",
            }
            for f, v in opts.items():
                if f in cons_fields and v is not None: doc[f] = v
            try:
                cons = safe_insert(doc)
                cons_ids.append(cons.name)
                log(f"Consultation: {PATIENTS[i]['name']} → {d['diag']}")
            except Exception as e:
                warn(f"Consultation {PATIENTS[i]['name']}: {e}")
                cons_ids.append(None)
                rx_ids.append(None)
                continue

        # Prescription
        try:
            existing_rx = frappe.db.get_value("Prescription", {rx_pat_link: pid}, "name")
        except:
            existing_rx = None

        if existing_rx:
            rx_ids.append(existing_rx)
            log(f"  Prescription exists: {PATIENTS[i]['name']}")
            continue

        doc = {"doctype": "Prescription", rx_pat_link: pid}
        opts = {
            "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
            "consultation": cons_ids[-1], "prescription_date": today(), "date": today(),
            "doctor": "Dr. Suresh Kumar", "status": "Active",
        }
        for f, v in opts.items():
            if f in rx_fields and v is not None: doc[f] = v

        try:
            child_tables = [f for f in frappe.get_meta("Prescription").fields if f.fieldtype == "Table"]
            med_field = child_tables[0].fieldname if child_tables else "medicines"
            med_child_dt = child_tables[0].options if child_tables else None
            med_child_fields = get_fields(med_child_dt) if med_child_dt else []
            print(f"  ℹ️  Medicine child table: '{med_field}', fields: {med_child_fields[:8]}")
        except:
            med_field = "medicines"
            med_child_fields = []

        try:
            rx = frappe.get_doc(doc)
            rx.flags.ignore_mandatory = True
            rx.flags.ignore_permissions = True
            for med in d["meds"]:
                all_possible = {
                    "medicine_name": med[0], "drug_name": med[0], "item": med[0], "medication": med[0],
                    "dosage": med[1], "dose": med[1],
                    "frequency": med[2],
                    "duration": str(med[3]), "duration_days": med[3],
                }
                row = {k: v for k, v in all_possible.items() if not med_child_fields or k in med_child_fields}
                rx.append(med_field, row)
            rx.insert(ignore_permissions=True)
            rx_ids.append(rx.name)
            log(f"  Prescription → {rx.name}")
        except Exception as e:
            warn(f"  Prescription {PATIENTS[i]['name']}: {e}")
            rx_ids.append(None)

    return cons_ids, rx_ids


# ─────────────────────────────────────────────
# LAB
# ─────────────────────────────────────────────

def create_lab_data(patient_ids, cons_ids):
    print("\n🔬 Creating Lab Data...")
    lr_f   = get_fields("Lab Request")
    lrp_f  = get_fields("Lab Report")
    lr_pat  = find_patient_link_field("Lab Request")
    lrp_pat = find_patient_link_field("Lab Report")

    data = [
        ("ECG Cardiac Enzymes Lipid Profile", "Troponin I 0.8 elevated LDL 160",   "Elevated cardiac enzymes. Cardiology review."),
        ("CBC Dengue NS1 Antigen IgM",        "Platelet 85000 low NS1 POSITIVE",    "Dengue confirmed. Monitor platelets."),
        ("HbA1c FBS PPBS KFT",               "HbA1c 9.2% FBS 280 mg/dL",          "Poorly controlled diabetes."),
        ("CBC CRP Urine Routine",             "WBC 14000 elevated CRP 48 mg/L",     "Raised inflammatory markers."),
        ("Uric Acid RA Factor CRP",           "Uric Acid 7.2 RA Factor Negative",   "Mild hyperuricemia OA confirmed."),
    ]

    for i in range(min(5, len(patient_ids))):
        pid = patient_ids[i]
        cons_id = cons_ids[i] if i < len(cons_ids) else None
        tests, results, conclusion = data[i]

        try:
            lr_name = frappe.db.get_value("Lab Request", {lr_pat: pid}, "name")
        except:
            lr_name = None

        if not lr_name:
            doc = {"doctype": "Lab Request", lr_pat: pid}
            opts = {
                "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
                "consultation": cons_id, "requested_date": today(), "date": today(),
                "requested_by": "Dr. Suresh Kumar",
                "tests_requested": tests, "tests": tests,
                "urgent": 1, "status": "Completed",
            }
            for f, v in opts.items():
                if f in lr_f and v is not None: doc[f] = v
            try:
                lr = safe_insert(doc)
                lr_name = lr.name
                log(f"Lab Request: {PATIENTS[i]['name']}")
            except Exception as e:
                warn(f"Lab Request: {e}")
                continue

        try:
            existing = frappe.db.get_value("Lab Report", {lrp_pat: pid}, "name")
        except:
            existing = None

        if not existing:
            doc = {"doctype": "Lab Report", lrp_pat: pid}
            opts = {
                "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
                "lab_request": lr_name, "report_date": today(), "date": today(),
                "technician": "Karthik Nair",
                "test_results": results, "results": results,
                "clinical_conclusion": conclusion, "conclusion": conclusion,
                "status": "Verified",
            }
            for f, v in opts.items():
                if f in lrp_f and v is not None: doc[f] = v
            try:
                safe_insert(doc)
                log(f"  Lab Report: {conclusion[:45]}")
            except Exception as e:
                warn(f"  Lab Report: {e}")


# ─────────────────────────────────────────────
# RADIOLOGY
# ─────────────────────────────────────────────

def create_radiology_data(patient_ids, cons_ids):
    print("\n📡 Creating Radiology Data...")
    rr_f   = get_fields("Radiology Request")
    rrp_f  = get_fields("Radiology Report")
    rr_pat  = find_patient_link_field("Radiology Request")
    rrp_pat = find_patient_link_field("Radiology Report")

    data = [
        (0, "Chest X-Ray and Echo",   "Cardiomegaly EF 45%",               "Dilated cardiomyopathy. Cardiology consult."),
        (3, "USG Abdomen and Pelvis", "Appendix 9mm periappendiceal fat",   "Acute appendicitis. Surgical review."),
        (4, "X-Ray Knee bilateral",   "Joint space narrowing osteophytes",  "Grade 3 OA bilateral knees."),
    ]

    for idx, scan, findings, impression in data:
        if idx >= len(patient_ids): continue
        pid = patient_ids[idx]
        cons_id = cons_ids[idx] if idx < len(cons_ids) else None

        try:
            rr_name = frappe.db.get_value("Radiology Request", {rr_pat: pid}, "name")
        except:
            rr_name = None

        if not rr_name:
            doc = {"doctype": "Radiology Request", rr_pat: pid}
            opts = {
                "patient_name": PATIENTS[idx]["name"], "full_name": PATIENTS[idx]["name"],
                "consultation": cons_id, "requested_date": today(), "date": today(),
                "requested_by": "Dr. Suresh Kumar",
                "scan_type": scan, "examination": scan,
                "status": "Completed",
            }
            for f, v in opts.items():
                if f in rr_f and v is not None: doc[f] = v
            try:
                rr = safe_insert(doc)
                rr_name = rr.name
                log(f"Radiology Request: {PATIENTS[idx]['name']} → {scan}")
            except Exception as e:
                warn(f"Radiology Request: {e}")
                continue

        try:
            existing = frappe.db.get_value("Radiology Report", {rrp_pat: pid}, "name")
        except:
            existing = None

        if not existing:
            doc = {"doctype": "Radiology Report", rrp_pat: pid}
            opts = {
                "patient_name": PATIENTS[idx]["name"], "full_name": PATIENTS[idx]["name"],
                "radiology_request": rr_name, "report_date": today(), "date": today(),
                "radiographer": "Deepa Menon",
                "findings": findings, "impression": impression,
                "status": "Verified",
            }
            for f, v in opts.items():
                if f in rrp_f and v is not None: doc[f] = v
            try:
                safe_insert(doc)
                log(f"  Radiology Report: {impression[:45]}")
            except Exception as e:
                warn(f"  Radiology Report: {e}")


# ─────────────────────────────────────────────
# PHARMACY
# ─────────────────────────────────────────────

def create_pharmacy_data(patient_ids, rx_ids):
    print("\n💊 Creating Pharmacy Records...")
    fields  = get_fields("Pharmacy Dispensing")
    pat_link = find_patient_link_field("Pharmacy Dispensing")

    for i in range(min(6, len(patient_ids))):
        pid = patient_ids[i]
        try:
            if frappe.db.get_value("Pharmacy Dispensing", {pat_link: pid}, "name"):
                log(f"Pharmacy exists: {PATIENTS[i]['name']}")
                continue
        except:
            pass
        doc = {"doctype": "Pharmacy Dispensing", pat_link: pid}
        opts = {
            "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
            "prescription": rx_ids[i] if i < len(rx_ids) else None,
            "dispense_date": today(), "date": today(),
            "pharmacist": "Venkat Rao", "status": "Dispensed",
            "total_amount": random.choice([150, 280, 420, 560, 175, 340]),
        }
        for f, v in opts.items():
            if f in fields and v is not None: doc[f] = v
        try:
            safe_insert(doc)
            log(f"Pharmacy: {PATIENTS[i]['name']} dispensed ✓")
        except Exception as e:
            warn(f"Pharmacy {PATIENTS[i]['name']}: {e}")


# ─────────────────────────────────────────────
# IPD
# ─────────────────────────────────────────────

def create_ipd_data(patient_ids):
    print("\n🛏️ Creating IPD Admissions...")
    fields   = get_fields("IPD Admission")
    pat_link = find_patient_link_field("IPD Admission")

    ipd_list = [
        (8, "COPD Exacerbation",          "General Ward A", "WARD-A-01", "Dr. Suresh Kumar"),
        (3, "Post-op Appendectomy Day 1", "Surgical Ward",  "WARD-C-01", "Dr. Ramesh Babu"),
    ]
    for idx, diag, ward, bed, doctor in ipd_list:
        if idx >= len(patient_ids): continue
        pid = patient_ids[idx]
        try:
            if frappe.db.get_value("IPD Admission", {pat_link: pid}, "name"):
                log(f"IPD exists: {PATIENTS[idx]['name']}")
                continue
        except:
            pass
        doc = {"doctype": "IPD Admission", pat_link: pid}
        opts = {
            "patient_name": PATIENTS[idx]["name"], "full_name": PATIENTS[idx]["name"],
            "admission_date": today(), "date": today(),
            "admitting_doctor": doctor, "doctor": doctor,
            "ward": ward, "bed_number": bed, "bed": bed,
            "diagnosis_at_admission": diag, "diagnosis": diag,
            "status": "Admitted",
        }
        for f, v in opts.items():
            if f in fields and v is not None: doc[f] = v
        try:
            safe_insert(doc)
            log(f"IPD: {PATIENTS[idx]['name']} → {ward} {bed}")
        except Exception as e:
            warn(f"IPD {PATIENTS[idx]['name']}: {e}")


# ─────────────────────────────────────────────
# ICU
# ─────────────────────────────────────────────

def create_icu_data(patient_ids):
    print("\n🚨 Creating ICU Monitoring...")
    fields   = get_fields("ICU Monitoring")
    pat_link = find_patient_link_field("ICU Monitoring")

    i = 9
    if i >= len(patient_ids): return
    pid = patient_ids[i]

    readings = [
        (96,120,80,88,37.2,"Stable","Nasal O2 2L"),
        (95,118,78,90,37.4,"Stable","Nasal O2 2L"),
        (93,125,85,94,37.8,"Guarded","Nasal O2 4L"),
    ]
    for j, r in enumerate(readings):
        doc = {"doctype": "ICU Monitoring", pat_link: pid}
        opts = {
            "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
            "monitoring_date": today(), "date": today(),
            "monitoring_time": f"{8+j*2:02d}:00:00", "time": f"{8+j*2:02d}:00:00",
            "spo2": r[0], "oxygen_saturation": r[0],
            "bp_systolic": r[1], "systolic": r[1],
            "bp_diastolic": r[2], "diastolic": r[2],
            "pulse": r[3], "heart_rate": r[3],
            "temperature": r[4],
            "condition": r[5], "status": r[5],
            "notes": r[6], "ventilator_support": r[6],
            "nurse": "Ramesh Babu",
        }
        for f, v in opts.items():
            if f in fields and v is not None: doc[f] = v
        try:
            safe_insert(doc)
            log(f"ICU [{j+1}]: SpO2 {r[0]}% BP {r[1]}/{r[2]} [{r[5]}]")
        except Exception as e:
            warn(f"ICU {j+1}: {e}")


# ─────────────────────────────────────────────
# NURSING TASKS
# ─────────────────────────────────────────────

def create_nursing_tasks(patient_ids):
    print("\n👩‍⚕️ Creating Nursing Tasks...")
    fields   = get_fields("Nursing Task")
    pat_link = find_patient_link_field("Nursing Task")

    tasks = [
        (0,"Injection",    "Injection Pantoprazole 40mg IV",      "Done"),
        (1,"IV Fluid",     "IV Normal Saline 500ml over 4 hours", "In Progress"),
        (2,"Monitoring",   "Blood sugar check every 6 hours",     "Pending"),
        (8,"Nebulization", "Duolin nebulization 4th hourly",      "In Progress"),
        (9,"Catheter Care","Foley catheter care",                 "Pending"),
    ]
    for idx, task_type, desc, status in tasks:
        if idx >= len(patient_ids): continue
        pid = patient_ids[idx]
        try:
            if frappe.db.get_value("Nursing Task", {pat_link: pid}, "name"): continue
        except:
            pass
        doc = {"doctype": "Nursing Task", pat_link: pid}
        opts = {
            "patient_name": PATIENTS[idx]["name"], "full_name": PATIENTS[idx]["name"],
            "task_date": today(), "date": today(),
            "task_type": task_type, "type": task_type,
            "task_description": desc, "description": desc, "task": desc,
            "status": status,
            "assigned_nurse": "Anitha Rajan", "nurse": "Anitha Rajan",
        }
        for f, v in opts.items():
            if f in fields and v is not None: doc[f] = v
        try:
            safe_insert(doc)
            log(f"Nursing: {PATIENTS[idx]['name']} → {desc[:35]} [{status}]")
        except Exception as e:
            warn(f"Nursing: {e}")


# ─────────────────────────────────────────────
# MASTER RUN
# ─────────────────────────────────────────────

def run_full_setup():
    print("\n" + "=" * 65)
    print("  🏥 MEDICARE HOSPITAL - SETUP v4")
    print("=" * 65)

    patient_ids = create_patients()
    if not patient_ids:
        warn("No patients created — stopping.")
        return

    appointment_ids = create_appointments(patient_ids)

    create_vital_signs(patient_ids)

    cons_ids, rx_ids = [], []
    try:
        cons_ids, rx_ids = create_consultations(patient_ids, appointment_ids)
    except Exception as e:
        warn(f"Consultations: {e}")

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
  Password for all users: Medicare@2026
  registration@medicare.com  →  /registration-portal
  nurse@medicare.com         →  /nurse-portal
  doctor@medicare.com        →  /doctor-portal
  lab@medicare.com           →  /lab-portal
  radiology@medicare.com     →  /radiology-portal
  pharmacy@medicare.com      →  /pharmacy-portal
  ward@medicare.com          →  /ipd-portal
  icu@medicare.com           →  /icu-portal
""")
