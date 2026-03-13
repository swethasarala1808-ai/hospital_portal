"""
🏥 Medicare Hospital Portal - Setup Script v5
Fix: Use email addresses for Doctor/Nurse/Pharmacist Link fields
Run: bench --site hospital.localhost execute hospital_portal.hospital_setup_v5.run_full_setup
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

# Use EMAIL addresses — these are the actual User records in Frappe
DOCTOR_EMAIL    = "doctor@medicare.com"
NURSE_EMAIL     = "nurse@medicare.com"
PHARMACIST_EMAIL= "pharmacy@medicare.com"
WARD_EMAIL      = "ward@medicare.com"
ICU_EMAIL       = "icu@medicare.com"
LAB_EMAIL       = "lab@medicare.com"
RADIO_EMAIL     = "radiology@medicare.com"

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

def find_patient_link_field(doctype):
    try:
        meta = frappe.get_meta(doctype)
        for f in meta.fields:
            if f.fieldtype == "Link" and f.options == "Patient Registration":
                return f.fieldname
        all_fields = [f.fieldname for f in meta.fields]
        for candidate in ["patient_id", "patient", "patient_registration", "reg_id"]:
            if candidate in all_fields:
                return candidate
    except:
        pass
    return "patient"

def find_user_link_field(doctype, role_hint):
    """Find field that links to User for a given role (doctor, nurse, etc.)"""
    try:
        meta = frappe.get_meta(doctype)
        # First: find Link field pointing to User
        user_fields = [f.fieldname for f in meta.fields if f.fieldtype == "Link" and f.options == "User"]
        if user_fields:
            # Pick the most relevant one based on hint
            for uf in user_fields:
                if role_hint.lower() in uf.lower():
                    return uf
            return user_fields[0]
        # Fallback: look by common name
        all_fields = [f.fieldname for f in meta.fields]
        hints = [role_hint, f"{role_hint}_name", f"assigned_{role_hint}",
                 "doctor", "physician", "nurse", "pharmacist", "technician", "radiographer"]
        for h in hints:
            if h in all_fields:
                return h
    except:
        pass
    return None

def safe_insert(doc_dict):
    doc = frappe.get_doc(doc_dict)
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_validate = True
    doc.flags.ignore_permissions = True
    doc.insert(ignore_permissions=True)
    return doc


# ─────────────────────────────────────────────
# PRINT FIELD MAP (diagnostic)
# ─────────────────────────────────────────────

def print_field_map():
    print("\n🔍 Doctype Field Diagnostics:")
    for dt in ["Consultation", "Lab Request", "Radiology Request",
               "Pharmacy Dispensing", "IPD Admission", "Nursing Task"]:
        try:
            meta = frappe.get_meta(dt)
            link_fields = [(f.fieldname, f.options) for f in meta.fields if f.fieldtype == "Link"]
            print(f"  {dt}: {link_fields}")
        except:
            pass


# ─────────────────────────────────────────────
# CONSULTATIONS + PRESCRIPTIONS
# ─────────────────────────────────────────────

def create_consultations(patient_ids, appointment_ids):
    print("\n👨‍⚕️ Creating Consultations & Prescriptions...")
    print_field_map()

    cons_fields   = get_fields("Consultation")
    rx_fields     = get_fields("Prescription")
    cons_pat_link = find_patient_link_field("Consultation")

    # Find doctor field in Consultation
    doctor_field = find_user_link_field("Consultation", "doctor")
    print(f"  ℹ️  Consultation: patient='{cons_pat_link}', doctor='{doctor_field}'")
    print(f"  ℹ️  All Consultation fields: {cons_fields}")

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

            # Build opts — try both name and email for doctor field
            opts = {
                "patient_name": PATIENTS[i]["name"],
                "full_name": PATIENTS[i]["name"],
                "appointment": appt_id,
                "consultation_date": today(), "date": today(),
                "diagnosis": d["diag"], "primary_diagnosis": d["diag"],
                "clinical_notes": d["notes"], "notes": d["notes"],
                "status": "Completed",
            }
            # Set doctor field using email (User link)
            if doctor_field and doctor_field in cons_fields:
                opts[doctor_field] = DOCTOR_EMAIL

            for f, v in opts.items():
                if f in cons_fields and v is not None:
                    doc[f] = v

            try:
                cons = safe_insert(doc)
                cons_ids.append(cons.name)
                log(f"Consultation: {PATIENTS[i]['name']} → {d['diag']}")
            except Exception as e:
                warn(f"Consultation {PATIENTS[i]['name']}: {e}")
                # Try without doctor field
                try:
                    doc2 = {k: v for k, v in doc.items() if k != doctor_field}
                    cons = safe_insert(doc2)
                    cons_ids.append(cons.name)
                    log(f"Consultation (no doctor): {PATIENTS[i]['name']} → {d['diag']}")
                except Exception as e2:
                    warn(f"Consultation failed: {e2}")
                    cons_ids.append(None)
                    rx_ids.append(None)
                    continue

        # Prescription
        rx_pat_link = find_patient_link_field("Prescription")
        try:
            existing_rx = frappe.db.get_value("Prescription", {rx_pat_link: pid}, "name")
        except:
            existing_rx = None

        if existing_rx:
            rx_ids.append(existing_rx)
            log(f"  Prescription exists: {PATIENTS[i]['name']}")
            continue

        rx_doctor_field = find_user_link_field("Prescription", "doctor")
        doc = {"doctype": "Prescription", rx_pat_link: pid}
        opts = {
            "patient_name": PATIENTS[i]["name"], "full_name": PATIENTS[i]["name"],
            "consultation": cons_ids[-1], "prescription_date": today(), "date": today(),
            "status": "Active",
        }
        if rx_doctor_field and rx_doctor_field in rx_fields:
            opts[rx_doctor_field] = DOCTOR_EMAIL
        for f, v in opts.items():
            if f in rx_fields and v is not None: doc[f] = v

        try:
            child_tables = [f for f in frappe.get_meta("Prescription").fields if f.fieldtype == "Table"]
            med_field = child_tables[0].fieldname if child_tables else "medicines"
            med_child_dt = child_tables[0].options if child_tables else None
            med_child_fields = get_fields(med_child_dt) if med_child_dt else []
        except:
            med_field = "medicines"; med_child_fields = []

        try:
            rx = frappe.get_doc(doc)
            rx.flags.ignore_mandatory = True
            rx.flags.ignore_permissions = True
            for med in d["meds"]:
                all_possible = {
                    "medicine_name": med[0], "drug_name": med[0], "item": med[0],
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
    lr_f    = get_fields("Lab Request")
    lrp_f   = get_fields("Lab Report")
    lr_pat  = find_patient_link_field("Lab Request")
    lrp_pat = find_patient_link_field("Lab Report")
    doc_field = find_user_link_field("Lab Request", "doctor")
    tech_field = find_user_link_field("Lab Report", "technician")
    print(f"  ℹ️  Lab Request: patient='{lr_pat}', doctor='{doc_field}'")
    print(f"  ℹ️  Lab Report: patient='{lrp_pat}', technician='{tech_field}'")

    data = [
        ("ECG Cardiac Enzymes Lipid Profile", "Troponin I 0.8 elevated LDL 160",  "Elevated cardiac enzymes. Cardiology review."),
        ("CBC Dengue NS1 Antigen IgM",        "Platelet 85000 low NS1 POSITIVE",   "Dengue confirmed. Monitor platelets."),
        ("HbA1c FBS PPBS KFT",               "HbA1c 9.2% FBS 280 mg/dL",         "Poorly controlled diabetes."),
        ("CBC CRP Urine Routine",             "WBC 14000 elevated CRP 48 mg/L",    "Raised inflammatory markers."),
        ("Uric Acid RA Factor CRP",           "Uric Acid 7.2 RA Factor Negative",  "Mild hyperuricemia OA confirmed."),
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
                "tests_requested": tests, "tests": tests,
                "urgent": 1, "status": "Completed",
            }
            if doc_field and doc_field in lr_f:
                opts[doc_field] = DOCTOR_EMAIL
            for f, v in opts.items():
                if f in lr_f and v is not None: doc[f] = v
            try:
                lr = safe_insert(doc)
                lr_name = lr.name
                log(f"Lab Request: {PATIENTS[i]['name']}")
            except Exception as e:
                # Try without doctor
                try:
                    doc2 = {k: v for k, v in doc.items() if k != doc_field}
                    lr = safe_insert(doc2)
                    lr_name = lr.name
                    log(f"Lab Request (no doctor): {PATIENTS[i]['name']}")
                except Exception as e2:
                    warn(f"Lab Request: {e2}")
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
                "test_results": results, "results": results,
                "clinical_conclusion": conclusion, "conclusion": conclusion,
                "status": "Verified",
            }
            if tech_field and tech_field in lrp_f:
                opts[tech_field] = LAB_EMAIL
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
    rr_f    = get_fields("Radiology Request")
    rrp_f   = get_fields("Radiology Report")
    rr_pat  = find_patient_link_field("Radiology Request")
    rrp_pat = find_patient_link_field("Radiology Report")
    doc_field  = find_user_link_field("Radiology Request", "doctor")
    rad_field  = find_user_link_field("Radiology Report", "radiographer")
    print(f"  ℹ️  Radiology Request: patient='{rr_pat}', doctor='{doc_field}'")

    data = [
        (0, "Chest X-Ray and Echo",   "Cardiomegaly EF 45%",              "Dilated cardiomyopathy. Cardiology consult."),
        (3, "USG Abdomen and Pelvis", "Appendix 9mm periappendiceal fat",  "Acute appendicitis. Surgical review."),
        (4, "X-Ray Knee bilateral",   "Joint space narrowing osteophytes", "Grade 3 OA bilateral knees."),
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
                "scan_type": scan, "examination": scan,
                "status": "Completed",
            }
            if doc_field and doc_field in rr_f:
                opts[doc_field] = DOCTOR_EMAIL
            for f, v in opts.items():
                if f in rr_f and v is not None: doc[f] = v
            try:
                rr = safe_insert(doc)
                rr_name = rr.name
                log(f"Radiology Request: {PATIENTS[idx]['name']} → {scan}")
            except Exception as e:
                try:
                    doc2 = {k: v for k, v in doc.items() if k != doc_field}
                    rr = safe_insert(doc2)
                    rr_name = rr.name
                    log(f"Radiology Request (no doctor): {PATIENTS[idx]['name']}")
                except Exception as e2:
                    warn(f"Radiology Request: {e2}")
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
                "findings": findings, "impression": impression,
                "status": "Verified",
            }
            if rad_field and rad_field in rrp_f:
                opts[rad_field] = RADIO_EMAIL
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
    fields    = get_fields("Pharmacy Dispensing")
    pat_link  = find_patient_link_field("Pharmacy Dispensing")
    pharm_field = find_user_link_field("Pharmacy Dispensing", "pharmacist")
    print(f"  ℹ️  Pharmacy: patient='{pat_link}', pharmacist='{pharm_field}'")
    print(f"  ℹ️  Pharmacy fields: {fields}")

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
            "status": "Dispensed",
            "total_amount": random.choice([150, 280, 420, 560, 175, 340]),
        }
        if pharm_field and pharm_field in fields:
            opts[pharm_field] = PHARMACIST_EMAIL
        for f, v in opts.items():
            if f in fields and v is not None: doc[f] = v

        try:
            safe_insert(doc)
            log(f"Pharmacy: {PATIENTS[i]['name']} dispensed ✓")
        except Exception as e:
            # Try without pharmacist field
            try:
                doc2 = {k: v for k, v in doc.items() if k != pharm_field}
                safe_insert(doc2)
                log(f"Pharmacy (no pharmacist): {PATIENTS[i]['name']} ✓")
            except Exception as e2:
                warn(f"Pharmacy {PATIENTS[i]['name']}: {e2}")


# ─────────────────────────────────────────────
# IPD
# ─────────────────────────────────────────────

def create_ipd_data(patient_ids):
    print("\n🛏️ Creating IPD Admissions...")
    fields    = get_fields("IPD Admission")
    pat_link  = find_patient_link_field("IPD Admission")
    doc_field = find_user_link_field("IPD Admission", "doctor")
    print(f"  ℹ️  IPD: patient='{pat_link}', doctor='{doc_field}'")

    ipd_list = [
        (8, "COPD Exacerbation",          "General Ward A", "WARD-A-01", DOCTOR_EMAIL),
        (3, "Post-op Appendectomy Day 1", "Surgical Ward",  "WARD-C-01", DOCTOR_EMAIL),
    ]
    for idx, diag, ward, bed, doctor_email in ipd_list:
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
            "ward": ward, "bed_number": bed, "bed": bed,
            "diagnosis_at_admission": diag, "diagnosis": diag,
            "status": "Admitted",
        }
        if doc_field and doc_field in fields:
            opts[doc_field] = doctor_email
        for f, v in opts.items():
            if f in fields and v is not None: doc[f] = v

        try:
            safe_insert(doc)
            log(f"IPD: {PATIENTS[idx]['name']} → {ward} {bed}")
        except Exception as e:
            try:
                doc2 = {k: v for k, v in doc.items() if k != doc_field}
                safe_insert(doc2)
                log(f"IPD (no doctor): {PATIENTS[idx]['name']} → {ward}")
            except Exception as e2:
                warn(f"IPD {PATIENTS[idx]['name']}: {e2}")


# ─────────────────────────────────────────────
# NURSING TASKS
# ─────────────────────────────────────────────

def create_nursing_tasks(patient_ids):
    print("\n👩‍⚕️ Creating Nursing Tasks...")
    fields    = get_fields("Nursing Task")
    pat_link  = find_patient_link_field("Nursing Task")
    nurse_field = find_user_link_field("Nursing Task", "nurse")
    print(f"  ℹ️  Nursing Task: patient='{pat_link}', nurse='{nurse_field}'")
    print(f"  ℹ️  Nursing Task fields: {fields}")

    tasks = [
        (0, "Injection",    "Injection Pantoprazole 40mg IV",      "Done"),
        (1, "IV Fluid",     "IV Normal Saline 500ml over 4 hours", "In Progress"),
        (2, "Monitoring",   "Blood sugar check every 6 hours",     "Pending"),
        (8, "Nebulization", "Duolin nebulization 4th hourly",      "In Progress"),
        (9, "Catheter Care","Foley catheter care",                 "Pending"),
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
        }
        if nurse_field and nurse_field in fields:
            opts[nurse_field] = NURSE_EMAIL
        for f, v in opts.items():
            if f in fields and v is not None: doc[f] = v

        try:
            safe_insert(doc)
            log(f"Nursing: {PATIENTS[idx]['name']} → {desc[:35]} [{status}]")
        except Exception as e:
            try:
                doc2 = {k: v for k, v in doc.items() if k != nurse_field}
                safe_insert(doc2)
                log(f"Nursing (no nurse field): {PATIENTS[idx]['name']} [{status}]")
            except Exception as e2:
                warn(f"Nursing {PATIENTS[idx]['name']}: {e2}")


# ─────────────────────────────────────────────
# MASTER RUN
# ─────────────────────────────────────────────

def run_full_setup():
    print("\n" + "=" * 65)
    print("  🏥 MEDICARE HOSPITAL - SETUP v5 (final fix)")
    print("=" * 65)

    # Patients already created — just fetch their IDs
    print("\n📋 Loading existing patients...")
    patient_ids = []
    appointment_ids = []

    for p in PATIENTS:
        pid = frappe.db.get_value("Patient Registration", {"full_name": p["name"]}, "name")
        if pid:
            patient_ids.append(pid)
            log(f"Found: {p['name']} → {pid}")
        else:
            warn(f"Patient not found: {p['name']} — run v4 first")

    if not patient_ids:
        warn("No patients found. Run v4 first.")
        return

    # Load existing appointments
    print("\n🎫 Loading existing appointments...")
    from hospital_portal.hospital_setup_v4 import find_patient_link_field as fplf
    appt_pat = fplf("Appointment")
    for pid in patient_ids:
        try:
            appt = frappe.db.get_value("Appointment", {appt_pat: pid}, "name")
            appointment_ids.append(appt)
        except:
            appointment_ids.append(None)

    # Now run only the failed steps
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

    try: create_nursing_tasks(patient_ids)
    except Exception as e: warn(f"Nursing: {e}")

    frappe.db.commit()

    print("\n" + "=" * 65)
    print("  ✅ ALL DONE! Your dashboard should now show full data.")
    print("=" * 65)
    print("""
  Open: http://hospital.localhost:8001/hospital-dashboard
  
  Department logins (password: Medicare@2026):
  registration@medicare.com  →  /registration-portal
  nurse@medicare.com         →  /nurse-portal
  doctor@medicare.com        →  /doctor-portal
  lab@medicare.com           →  /lab-portal
  radiology@medicare.com     →  /radiology-portal
  pharmacy@medicare.com      →  /pharmacy-portal
  ward@medicare.com          →  /ipd-portal
  icu@medicare.com           →  /icu-portal
""")
