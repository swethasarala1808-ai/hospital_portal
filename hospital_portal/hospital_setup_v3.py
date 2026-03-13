"""
🏥 Medicare Hospital Portal - Setup Script v3
Fix: phone country code, gender Select options, mandatory field bypass
Run: bench --site hospital.localhost execute hospital_portal.hospital_setup_v3.run_full_setup
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


def get_field_options(doctype, fieldname):
    """Get allowed Select options for a field"""
    try:
        meta = frappe.get_meta(doctype)
        for f in meta.fields:
            if f.fieldname == fieldname and f.options:
                return [o.strip() for o in f.options.split("\n") if o.strip()]
    except:
        pass
    return []


def get_fields(doctype):
    try:
        return [f.fieldname for f in frappe.get_meta(doctype).fields]
    except:
        return []


def safe_insert(doc_dict):
    """Insert with ignore_mandatory=True to bypass required field validation"""
    doc = frappe.get_doc(doc_dict)
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_validate = True
    doc.flags.ignore_permissions = True
    doc.insert(ignore_permissions=True)
    return doc


# ─────────────────────────────────────────────
# PATIENTS + APPOINTMENTS
# ─────────────────────────────────────────────

def create_patients_and_appointments():
    print("\n📋 Creating Patient Registrations & Appointments...")

    # Detect fields
    pat_fields = get_fields("Patient Registration")
    appt_fields = get_fields("Appointment")

    # Detect gender options
    gender_options = get_field_options("Patient Registration", "gender")
    print(f"  ℹ️  Gender options in your doctype: {gender_options}")

    # Detect phone field name
    phone_field = None
    for f in ["phone", "mobile", "mobile_no", "contact_number"]:
        if f in pat_fields:
            phone_field = f
            break

    # Detect visit_type options
    visit_options = get_field_options("Patient Registration", "visit_type")
    visit_val = visit_options[0] if visit_options else None
    print(f"  ℹ️  visit_type options: {visit_options}")

    # Detect status options
    status_options = get_field_options("Patient Registration", "status")
    status_val = status_options[0] if status_options else "Registered"
    print(f"  ℹ️  status options: {status_options}")

    patient_ids = []
    appointment_ids = []

    doctors = ["Dr. Suresh Kumar", "Dr. Priya Arun", "Dr. Ramesh Babu", "Dr. Meena Pillai"]
    specialties = ["General Medicine", "Cardiology", "Orthopedics", "Dermatology"]

    for i, p in enumerate(PATIENTS):
        # Map gender to available options
        if gender_options:
            if p["gender"] == "Male":
                gender_val = next((o for o in gender_options if "male" in o.lower() and "female" not in o.lower()), gender_options[0])
            else:
                gender_val = next((o for o in gender_options if "female" in o.lower()), gender_options[0])
        else:
            gender_val = p["gender"]

        # Check if already exists
        existing = frappe.db.get_value("Patient Registration", {"full_name": p["name"]}, "name")
        if existing:
            patient_ids.append(existing)
            log(f"Patient exists: {p['name']} → {existing}")
        else:
            doc = {
                "doctype": "Patient Registration",
                "full_name": p["name"],
            }

            # Add fields that exist, safely
            optional = {
                "gender": gender_val,
                "date_of_birth": f"{2026 - p['age']}-01-01",
                "blood_group": p["blood"],
                "chief_complaint": p["complaint"],
                "registration_date": today(),
                "status": status_val,
            }
            if visit_val and "visit_type" in pat_fields:
                optional["visit_type"] = visit_val

            # Phone with country code
            if phone_field:
                optional[phone_field] = p["phone"]

            for f, v in optional.items():
                if f in pat_fields:
                    doc[f] = v

            try:
                pat = safe_insert(doc)
                patient_ids.append(pat.name)
                log(f"Patient: {p['name']} → {pat.name}")
            except Exception as e:
                warn(f"Patient {p['name']} error: {e}")
                # Last resort: only full_name
                try:
                    pat = safe_insert({"doctype": "Patient Registration", "full_name": p["name"]})
                    patient_ids.append(pat.name)
                    log(f"Patient (name only): {p['name']} → {pat.name}")
                except Exception as e2:
                    warn(f"Patient {p['name']} complete fail: {e2}")
                    continue

        pid = patient_ids[-1]

        # Appointment
        existing_appt = frappe.db.get_value("Appointment", {"patient": pid}, "name")
        if existing_appt:
            appointment_ids.append(existing_appt)
            log(f"  Token exists for {p['name']}")
            continue

        # Detect appointment status options
        appt_status_opts = get_field_options("Appointment", "status")
        appt_status = "Scheduled" if not appt_status_opts else appt_status_opts[0]

        appt_doc = {"doctype": "Appointment", "patient": pid}
        appt_opts = {
            "patient_name": p["name"], "full_name": p["name"],
            "appointment_date": today(), "date": today(),
            "appointment_time": f"{(9 + i) % 24:02d}:00:00",
            "doctor": doctors[i % 4],
            "department": specialties[i % 4],
            "token_number": i + 1,
            "status": appt_status,
            "consultation_fee": 500,
        }
        for f, v in appt_opts.items():
            if f in appt_fields:
                appt_doc[f] = v

        try:
            appt = safe_insert(appt_doc)
            appointment_ids.append(appt.name)
            log(f"  Token #{i+1} → {appt.name}")
        except Exception as e:
            warn(f"  Token for {p['name']}: {e}")
            appointment_ids.append(None)

    return patient_ids, appointment_ids


# ─────────────────────────────────────────────
# VITAL SIGNS
# ─────────────────────────────────────────────

def create_vital_signs(patient_ids):
    print("\n🩺 Creating Vital Signs...")
    fields = get_fields("Vital Signs")
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
    triage_opts = get_field_options("Vital Signs", "triage_level") or get_field_options("Vital Signs", "triage")

    for i, pid in enumerate(patient_ids[:8]):
        if frappe.db.exists("Vital Signs", {"patient": pid}):
            log(f"Vitals exist: {PATIENTS[i]['name']}")
            continue
        d = vitals[i]

        # Map triage
        triage_val = d[7]
        if triage_opts:
            triage_val = next((o for o in triage_opts if d[7].lower() in o.lower()), triage_opts[0])

        doc = {"doctype": "Vital Signs", "patient": pid}
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

    data = [
        {"diag": "Hypertensive Heart Disease",      "notes": "Chest pain ECG changes. Start amlodipine.",    "meds": [("Amlodipine","5mg","Once daily",30),("Aspirin","75mg","Once daily",30)]},
        {"diag": "Viral Fever Dengue Suspected",    "notes": "Fever 38.5C x 3 days. Dengue NS1 ordered.",   "meds": [("Paracetamol","500mg","Three times daily",5),("ORS","1 sachet","Three times daily",5)]},
        {"diag": "Type 2 Diabetes Uncontrolled",    "notes": "FBS 280. HbA1c ordered. Increase Metformin.", "meds": [("Metformin","1000mg","Twice daily",30),("Glipizide","5mg","Once daily",30)]},
        {"diag": "Acute Appendicitis Suspected",    "notes": "RIF pain USG ordered. Surgical consult.",     "meds": [("Inj Buscopan","20mg","Stat",1)]},
        {"diag": "Osteoarthritis Knee Bilateral",   "notes": "Grade 3 OA. Physio and NSAID.",               "meds": [("Diclofenac","50mg","Twice daily",15),("Calcium D3","500mg","Once daily",30)]},
        {"diag": "Tension Headache Hypertension",   "notes": "BP 125/82. Lifestyle advice given.",          "meds": [("Paracetamol","650mg","As needed",10),("Telmisartan","40mg","Once daily",30)]},
        {"diag": "Essential Hypertension",          "notes": "BP 150/98. Continue medications.",            "meds": [("Amlodipine","10mg","Once daily",30),("Losartan","50mg","Once daily",30)]},
        {"diag": "Allergic Dermatitis",             "notes": "Pruritic rash. Antihistamine started.",       "meds": [("Cetirizine","10mg","Once daily",10),("Betamethasone Cream","0.1%","Twice daily",1)]},
    ]

    cons_ids, rx_ids = [], []

    for i, pid in enumerate(patient_ids[:8]):
        d = data[i]
        appt_id = appointment_ids[i] if i < len(appointment_ids) else None

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
                cons = safe_insert(doc)
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
            continue

        doc = {"doctype": "Prescription", "patient": pid}
        opts = {
            "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
            "consultation": cons_ids[-1], "prescription_date": today(), "date": today(),
            "doctor": "Dr. Suresh Kumar", "status": "Active",
        }
        for f, v in opts.items():
            if f in rx_fields and v is not None: doc[f] = v

        # Find child table for medicines
        try:
            child_tables = [f for f in frappe.get_meta("Prescription").fields if f.fieldtype == "Table"]
            med_field = child_tables[0].fieldname if child_tables else "medicines"
            med_child_dt = child_tables[0].options if child_tables else None
            med_child_fields = get_fields(med_child_dt) if med_child_dt else []
            print(f"  ℹ️  Prescription child table: '{med_field}' ({med_child_dt}), fields: {med_child_fields[:10]}")
        except:
            med_field = "medicines"
            med_child_fields = []

        try:
            rx = frappe.get_doc(doc)
            rx.flags.ignore_mandatory = True
            rx.flags.ignore_permissions = True
            for med in d["meds"]:
                row = {}
                all_possible = {
                    "medicine_name": med[0], "drug_name": med[0], "item": med[0],
                    "medication": med[0], "name1": med[0],
                    "dosage": med[1], "dose": med[1], "strength": med[1],
                    "frequency": med[2], "route": "Oral",
                    "duration": str(med[3]), "duration_days": med[3],
                    "period": f"{med[3]} Days",
                }
                if med_child_fields:
                    row = {k: v for k, v in all_possible.items() if k in med_child_fields}
                else:
                    row = all_possible  # try all
                rx.append(med_field, row)
            rx.insert(ignore_permissions=True)
            rx_ids.append(rx.name)
            log(f"  Prescription: {len(d['meds'])} medicines → {rx.name}")
        except Exception as e:
            warn(f"  Prescription {PATIENTS[i]['name']}: {e}")
            rx_ids.append(None)

    return cons_ids, rx_ids


# ─────────────────────────────────────────────
# LAB
# ─────────────────────────────────────────────

def create_lab_data(patient_ids, cons_ids):
    print("\n🔬 Creating Lab Data...")
    lr_f  = get_fields("Lab Request")
    lrp_f = get_fields("Lab Report")

    data = [
        ("ECG Cardiac Enzymes Lipid Profile",  "Troponin I 0.8 ng/mL elevated LDL 160",  "Elevated cardiac enzymes. Cardiology review."),
        ("CBC Dengue NS1 Antigen Dengue IgM",  "Platelet 85000 low Dengue NS1 POSITIVE",  "Dengue confirmed. Monitor platelets daily."),
        ("HbA1c FBS PPBS KFT",                 "HbA1c 9.2% FBS 280 mg/dL",               "Poorly controlled diabetes."),
        ("CBC CRP Urine Routine",              "WBC 14000 elevated CRP 48 mg/L",          "Raised inflammatory markers."),
        ("Uric Acid RA Factor CRP",            "Uric Acid 7.2 mg/dL RA Factor Negative", "Mild hyperuricemia OA confirmed."),
    ]

    for i in range(min(5, len(patient_ids))):
        pid = patient_ids[i]
        cons_id = cons_ids[i] if i < len(cons_ids) else None
        tests, results, conclusion = data[i]

        lr_name = frappe.db.get_value("Lab Request", {"patient": pid}, "name")
        if not lr_name:
            doc = {"doctype": "Lab Request", "patient": pid}
            opts = {
                "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
                "consultation": cons_id, "requested_date": today(), "date": today(),
                "requested_by": "Dr. Suresh Kumar",
                "tests_requested": tests, "tests": tests, "test_name": tests,
                "urgent": 1, "status": "Completed",
            }
            for f, v in opts.items():
                if f in lr_f and v is not None: doc[f] = v
            try:
                lr = safe_insert(doc)
                lr_name = lr.name
                log(f"Lab Request: {PATIENTS[i]['name']}")
            except Exception as e:
                warn(f"Lab Request {PATIENTS[i]['name']}: {e}")
                continue

        if not frappe.db.exists("Lab Report", {"patient": pid}):
            doc = {"doctype": "Lab Report", "patient": pid}
            opts = {
                "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
                "lab_request": lr_name, "report_date": today(), "date": today(),
                "technician": "Karthik Nair", "lab_technician": "Karthik Nair",
                "test_results": results, "results": results, "result": results,
                "clinical_conclusion": conclusion, "conclusion": conclusion, "remarks": conclusion,
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
    rr_f  = get_fields("Radiology Request")
    rrp_f = get_fields("Radiology Report")

    data = [
        (0, "Chest X-Ray and Echo",      "Cardiomegaly EF 45%",                  "Dilated cardiomyopathy. Cardiology consult."),
        (3, "USG Abdomen and Pelvis",    "Appendix 9mm periappendiceal stranding","Acute appendicitis. Surgical review."),
        (4, "X-Ray Knee bilateral",      "Joint space narrowing osteophytes",     "Grade 3 OA bilateral knees."),
    ]

    for idx, scan, findings, impression in data:
        if idx >= len(patient_ids): continue
        pid = patient_ids[idx]
        cons_id = cons_ids[idx] if idx < len(cons_ids) else None

        rr_name = frappe.db.get_value("Radiology Request", {"patient": pid}, "name")
        if not rr_name:
            doc = {"doctype": "Radiology Request", "patient": pid}
            opts = {
                "patient_name": PATIENTS[idx]["name"], "full_name": PATIENTS[idx]["name"],
                "consultation": cons_id, "requested_date": today(), "date": today(),
                "requested_by": "Dr. Suresh Kumar",
                "scan_type": scan, "examination": scan, "modality": scan,
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

        if not frappe.db.exists("Radiology Report", {"patient": pid}):
            doc = {"doctype": "Radiology Report", "patient": pid}
            opts = {
                "patient_name": PATIENTS[idx]["name"], "full_name": PATIENTS[idx]["name"],
                "radiology_request": rr_name, "report_date": today(), "date": today(),
                "radiographer": "Deepa Menon",
                "findings": findings, "report": findings,
                "impression": impression, "conclusion": impression,
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
    fields = get_fields("Pharmacy Dispensing")
    for i in range(min(6, len(patient_ids))):
        pid = patient_ids[i]
        if frappe.db.exists("Pharmacy Dispensing", {"patient": pid}): continue
        doc = {"doctype": "Pharmacy Dispensing", "patient": pid}
        opts = {
            "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
            "prescription": rx_ids[i] if i < len(rx_ids) else None,
            "dispense_date": today(), "date": today(),
            "pharmacist": "Venkat Rao",
            "status": "Dispensed",
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
    fields = get_fields("IPD Admission")
    ipd_list = [
        (8, "COPD Exacerbation",         "General Ward A", "WARD-A-01", "Dr. Suresh Kumar"),
        (3, "Post-op Appendectomy Day 1","Surgical Ward",  "WARD-C-01", "Dr. Ramesh Babu"),
    ]
    for idx, diag, ward, bed, doctor in ipd_list:
        if idx >= len(patient_ids): continue
        pid = patient_ids[idx]
        if frappe.db.exists("IPD Admission", {"patient": pid}):
            log(f"IPD exists: {PATIENTS[idx]['name']}")
            continue
        doc = {"doctype": "IPD Admission", "patient": pid}
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
    fields = get_fields("ICU Monitoring")
    i = 9
    pid = patient_ids[i]
    readings = [
        (96,120,80,88,37.2,"Stable","Nasal O2 2L"),
        (95,118,78,90,37.4,"Stable","Nasal O2 2L"),
        (93,125,85,94,37.8,"Guarded","Nasal O2 4L"),
    ]
    for j, r in enumerate(readings):
        doc = {"doctype": "ICU Monitoring", "patient": pid}
        opts = {
            "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
            "monitoring_date": today(), "date": today(),
            "monitoring_time": f"{8+j*2:02d}:00:00", "time": f"{8+j*2:02d}:00:00",
            "spo2": r[0], "oxygen_saturation": r[0],
            "bp_systolic": r[1], "systolic": r[1],
            "bp_diastolic": r[2], "diastolic": r[2],
            "pulse": r[3], "heart_rate": r[3],
            "temperature": r[4],
            "condition": r[5], "patient_condition": r[5], "status": r[5],
            "ventilator_support": r[6], "support": r[6], "notes": r[6],
            "nurse": "Ramesh Babu",
        }
        for f, v in opts.items():
            if f in fields and v is not None: doc[f] = v
        try:
            safe_insert(doc)
            log(f"ICU [{j+1}]: {PATIENTS[i]['name']} SpO2 {r[0]}% BP {r[1]}/{r[2]}")
        except Exception as e:
            warn(f"ICU {j+1}: {e}")


# ─────────────────────────────────────────────
# NURSING TASKS
# ─────────────────────────────────────────────

def create_nursing_tasks(patient_ids):
    print("\n👩‍⚕️ Creating Nursing Tasks...")
    fields = get_fields("Nursing Task")
    tasks = [
        (0,"Injection",   "Injection Pantoprazole 40mg IV",     "Done"),
        (1,"IV Fluid",    "IV Normal Saline 500ml over 4 hours","In Progress"),
        (2,"Monitoring",  "Blood sugar check every 6 hours",    "Pending"),
        (8,"Nebulization","Duolin nebulization 4th hourly",      "In Progress"),
        (9,"Catheter Care","Foley catheter care",               "Pending"),
    ]
    for idx, task_type, desc, status in tasks:
        if idx >= len(patient_ids): continue
        pid = patient_ids[idx]
        if frappe.db.exists("Nursing Task", {"patient": pid}): continue
        doc = {"doctype": "Nursing Task", "patient": pid}
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
            log(f"Nursing Task: {PATIENTS[idx]['name']} → {desc[:35]} [{status}]")
        except Exception as e:
            warn(f"Nursing Task: {e}")


# ─────────────────────────────────────────────
# MASTER RUN
# ─────────────────────────────────────────────

def run_full_setup():
    print("\n" + "=" * 65)
    print("  🏥 MEDICARE HOSPITAL - SETUP v3")
    print("=" * 65)

    steps = [
        ("Patients + Appointments", lambda: create_patients_and_appointments()),
        ("Vital Signs",             lambda pid, _: create_vital_signs(pid)),
        ("Consultations",           lambda pid, appt: create_consultations(pid, appt)),
        ("Lab",                     lambda pid, cons: create_lab_data(pid, cons)),
        ("Radiology",               lambda pid, cons: create_radiology_data(pid, cons)),
        ("Pharmacy",                lambda pid, rx: create_pharmacy_data(pid, rx)),
        ("IPD",                     lambda pid, _: create_ipd_data(pid)),
        ("ICU",                     lambda pid, _: create_icu_data(pid)),
        ("Nursing Tasks",           lambda pid, _: create_nursing_tasks(pid)),
    ]

    try:
        patient_ids, appointment_ids = create_patients_and_appointments()
    except Exception as e:
        warn(f"Patients failed: {e}")
        return

    if not patient_ids:
        warn("No patients — stopping.")
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
    print("  ✅ DONE! Check your dashboard now.")
    print("=" * 65)
    print("""
  🔐 All department passwords: Medicare@2026
  registration@medicare.com  →  /registration-portal
  nurse@medicare.com         →  /nurse-portal
  doctor@medicare.com        →  /doctor-portal
  lab@medicare.com           →  /lab-portal
  radiology@medicare.com     →  /radiology-portal
  pharmacy@medicare.com      →  /pharmacy-portal
  ward@medicare.com          →  /ipd-portal
  icu@medicare.com           →  /icu-portal
""")
