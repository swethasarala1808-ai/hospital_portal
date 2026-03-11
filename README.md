# 🏥 Hospital Portal

> **Complete Hospital Management System built on Frappe/ERPNext**
> Separate app from `rena_portal` (Rehabilitation Centre) — Different site, different GitHub repo.

---

## 🏗️ What This App Does

A full hospital management system covering **8 departments** with role-based portals:

| # | Department | Portal Route | Role |
|---|-----------|-------------|------|
| 1 | Registration / Front Office | `/registration-portal` | Registration Staff |
| 2 | Nursing / Triage | `/nurse-portal` | Nurse |
| 3 | Consultation / Doctor | `/doctor-portal` | Doctor |
| 4 | Laboratory | `/lab-portal` | Lab Technician |
| 5 | Radiology | `/radiology-portal` | Radiographer |
| 6 | Pharmacy | `/pharmacy-portal` | Pharmacist |
| 7 | IPD / Inpatient Ward | `/ipd-portal` | Ward Nurse |
| 8 | ICU | `/icu-portal` | ICU Nurse |
| ⭐ | Hospital Head Dashboard | `/hospital-dashboard` | Hospital Head |

---

## 🚀 Installation

### Prerequisites
- Frappe Bench installed
- ERPNext installed on bench

### Steps

```bash
cd ~/frappe-bench

# 1. Get the app
bench get-app https://github.com/YOUR_USERNAME/hospital_portal --branch main

# 2. Create new site (SEPARATE from rena_portal)
bench new-site hospital.localhost \
  --db-name hospital_db \
  --admin-password admin123

# 3. Install apps on the new site
bench --site hospital.localhost install-app frappe
bench --site hospital.localhost install-app erpnext
bench --site hospital.localhost install-app hospital_portal

# 4. Run migrations
bench --site hospital.localhost migrate

# 5. Start
bench start
```

Visit: `http://hospital.localhost:8000`

---

## 🗂️ App Structure

```
hospital_portal/
├── hooks.py                    # Portal menus, events, roles
├── setup/
│   └── install.py              # Auto-creates roles & beds on install
├── doctype/
│   ├── patient_registration/   # Dept 1: PAT-YYYY-NNNNN
│   ├── appointment/            # Dept 1: Token generation
│   ├── vital_signs/            # Dept 2: BP, Temp, SpO2, Height, Weight
│   ├── nursing_task/           # Dept 2: Injections, IV, dressing tasks
│   ├── consultation/           # Dept 3: Doctor's notes, diagnosis, orders
│   ├── prescription/           # Dept 3: Medicines → Pharmacy + Nursing
│   ├── lab_request/            # Dept 4: Lab orders
│   ├── lab_report/             # Dept 4: Results uploaded to patient
│   ├── radiology_request/      # Dept 5: X-Ray, ECG, CT, MRI orders
│   ├── radiology_report/       # Dept 5: Reports + images
│   ├── pharmacy_dispensing/    # Dept 6: Dispense + ERPNext stock
│   ├── ipd_admission/          # Dept 7: Admit, bed allocation
│   ├── bed_management/         # Dept 7: Bed status tracking
│   └── icu_monitoring/         # Dept 8: Hourly ICU charts
├── www/
│   ├── hospital-dashboard.html # Hospital Head view
│   ├── registration-portal.html
│   ├── nurse-portal.html
│   ├── doctor-portal.html
│   ├── lab-portal.html
│   ├── radiology-portal.html
│   ├── pharmacy-portal.html
│   ├── ipd-portal.html
│   └── icu-portal.html
└── public/
    ├── css/hospital.css
    └── js/hospital.js
```

---

## 🔄 Patient Journey Workflow

```
Patient Arrives
   │
   ▼  1️⃣ REGISTRATION
   Register → Patient ID generated (PAT-YYYY-NNNNN)
   Appointment booked → Token generated → Receipt printed
   │
   ▼  2️⃣ NURSING TRIAGE
   Nurse scans Patient ID → Records vitals (BP, Temp, Weight, SpO2)
   Triage level assigned (Green / Yellow / Orange / Red)
   │
   ▼  3️⃣ CONSULTATION
   Doctor sees vitals → Examines → Diagnosis
   Doctor can ORDER:
   ├──► Lab Tests    → Lab Request → Lab processes → Lab Report ↩️ to Patient
   ├──► Radiology    → Radiology Request → Scan → Report ↩️ to Patient
   ├──► Prescription → Pharmacy Dispensing (ERPNext stock used)
   ├──► Nursing Task → Nurse gets notified (injection/IV/dressing)
   └──► Admit        → IPD Admission → Bed allocated
   │
   ▼  7️⃣ IPD (if admitted)
   Bed assigned → Daily rounds → Medication administered
   │
   ▼  8️⃣ ICU (if critical)
   Hourly monitoring → Ventilator management → Stabilize
   │
   ▼  DISCHARGE
   Discharge summary → Bill generated (ERPNext billing)
```

---

## 👥 Roles Created on Install

```
Hospital Head        → Full access, all departments
Registration Staff   → Patient registration, appointments, tokens
Nurse                → Vital signs, nursing tasks
Doctor               → Consultations, prescriptions, orders
Lab Technician       → Lab requests, reports
Pathologist          → Lab verification
Radiographer         → Radiology requests, reports
Radiologist          → Radiology verification
Pharmacist           → Prescription dispensing, stock
Ward Nurse           → IPD monitoring
ICU Nurse            → ICU monitoring
Intensivist          → ICU management
```

---

## 🏥 Two Clinic Modes

In **Hospital Settings** doctype, set `clinic_mode`:

| Mode | Departments Active |
|------|--------------------|
| `Hospital` | All 8 departments |
| `Clinic` | Registration + Consultation + Pharmacy only |

---

## 📋 Key Doctypes

| Doctype | Auto ID Format | Department |
|---------|---------------|-----------|
| Patient Registration | PAT-YYYY-NNNNN | Registration |
| Appointment | APT-YYYY-NNNNN | Registration |
| Vital Signs | VS-YYYY-NNNNN | Nursing |
| Nursing Task | NT-YYYY-NNNNN | Nursing |
| Consultation | CONS-YYYY-NNNNN | Doctor |
| Prescription | RX-YYYY-NNNNN | Doctor |
| Lab Request | LR-YYYY-NNNNN | Laboratory |
| Lab Report | LRP-YYYY-NNNNN | Laboratory |
| Radiology Request | RR-YYYY-NNNNN | Radiology |
| Radiology Report | RRP-YYYY-NNNNN | Radiology |
| Pharmacy Dispensing | PD-YYYY-NNNNN | Pharmacy |
| IPD Admission | IPD-YYYY-NNNNN | IPD |
| Bed Management | BED-WARD-NNN | IPD |
| ICU Monitoring | ICU-YYYY-NNNNN | ICU |

---

## 🆚 vs rena_portal

| | rena_portal | hospital_portal |
|--|-------------|-----------------|
| Purpose | Rehabilitation Centre | Full Hospital |
| Site | rena.localhost | hospital.localhost |
| Departments | Rehab-specific | 8 hospital depts |
| GitHub Repo | rena_portal | hospital_portal (this repo) |

Both run in the same bench but on separate sites.

---

## License
MIT
