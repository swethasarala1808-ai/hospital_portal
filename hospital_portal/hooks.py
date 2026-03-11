app_name = "hospital_portal"
app_title = "Hospital Portal"
app_publisher = "Your Organization"
app_description = "Complete Hospital Management System — 8 Departments"
app_email = "admin@hospital.com"
app_license = "MIT"
app_version = "1.0.0"

# ─────────────────────────────────────────
# PORTAL MENU (visible per role on website)
# ─────────────────────────────────────────
standard_portal_menu_items = [
    {"title": "Hospital Dashboard", "route": "/hospital-dashboard", "role": "Hospital Head",      "idx": 1},
    {"title": "Registration Desk",  "route": "/registration-portal","role": "Registration Staff", "idx": 2},
    {"title": "Nursing Station",    "route": "/nurse-portal",        "role": "Nurse",              "idx": 3},
    {"title": "Doctor Console",     "route": "/doctor-portal",       "role": "Doctor",             "idx": 4},
    {"title": "Laboratory",         "route": "/lab-portal",          "role": "Lab Technician",     "idx": 5},
    {"title": "Radiology",          "route": "/radiology-portal",    "role": "Radiographer",       "idx": 6},
    {"title": "Pharmacy",           "route": "/pharmacy-portal",     "role": "Pharmacist",         "idx": 7},
    {"title": "IPD Ward",           "route": "/ipd-portal",          "role": "Ward Nurse",         "idx": 8},
    {"title": "ICU",                "route": "/icu-portal",          "role": "ICU Nurse",          "idx": 9},
]

# ─────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────
fixtures = [
    "Role",
    {"dt": "Custom Field", "filters": [["module", "=", "Hospital Portal"]]},
    "Workflow",
    "Workflow State",
    "Workflow Action Master",
    "Print Format",
]

# ─────────────────────────────────────────
# INSTALL / UNINSTALL
# ─────────────────────────────────────────
after_install  = "hospital_portal.setup.install.after_install"
after_migrate  = "hospital_portal.setup.install.after_migrate"
before_uninstall = "hospital_portal.setup.install.before_uninstall"

# ─────────────────────────────────────────
# PERMISSION QUERY (row-level security)
# ─────────────────────────────────────────
permission_query_conditions = {
    "Consultation":       "hospital_portal.permissions.get_doctor_conditions",
    "Lab Request":        "hospital_portal.permissions.get_lab_conditions",
    "Radiology Request":  "hospital_portal.permissions.get_radiology_conditions",
    "Pharmacy Dispensing":"hospital_portal.permissions.get_pharmacy_conditions",
    "ICU Monitoring":     "hospital_portal.permissions.get_icu_conditions",
}

# ─────────────────────────────────────────
# DOCUMENT EVENTS (auto-actions)
# ─────────────────────────────────────────
doc_events = {
    "Prescription": {
        "on_submit": [
            "hospital_portal.events.prescription.forward_to_pharmacy",
            "hospital_portal.events.prescription.forward_to_nursing",
        ]
    },
    "Lab Request": {
        "on_submit": "hospital_portal.events.lab.notify_lab_technician",
    },
    "Radiology Request": {
        "on_submit": "hospital_portal.events.radiology.notify_radiographer",
    },
    "Appointment": {
        "after_insert": "hospital_portal.events.appointment.generate_token",
    },
    "Patient Registration": {
        "after_insert": "hospital_portal.events.patient.generate_patient_id",
    },
    "IPD Admission": {
        "on_submit": "hospital_portal.events.ipd.allocate_bed",
        "on_cancel": "hospital_portal.events.ipd.release_bed",
    },
}

# ─────────────────────────────────────────
# SCHEDULED TASKS
# ─────────────────────────────────────────
scheduler_events = {
    "daily": [
        "hospital_portal.tasks.check_medicine_expiry",
        "hospital_portal.tasks.check_low_stock",
    ],
    "hourly": [
        "hospital_portal.tasks.send_icu_monitoring_reminders",
    ],
    "cron": {
        "0 8 * * *": ["hospital_portal.tasks.daily_appointment_summary"],
    }
}

# ─────────────────────────────────────────
# WEBSITE / PORTAL
# ─────────────────────────────────────────
website_context = {
    "splash_image": "/assets/hospital_portal/images/hospital-logo.png",
    "favicon": "/assets/hospital_portal/images/favicon.ico",
}

website_route_rules = [
    {"from_route": "/patient/<patient_id>", "to_route": "patient-file"},
]

# ─────────────────────────────────────────
# JINJA METHODS (available in HTML templates)
# ─────────────────────────────────────────
jinja = {
    "methods": [
        "hospital_portal.utils.get_patient_journey",
        "hospital_portal.utils.get_department_stats",
        "hospital_portal.utils.get_bed_occupancy",
    ]
}

# ─────────────────────────────────────────
# OVERRIDE FORMS (custom JS per doctype)
# ─────────────────────────────────────────
doctype_js = {
    "Patient Registration": "public/js/patient_registration.js",
    "Appointment":          "public/js/appointment.js",
    "Consultation":         "public/js/consultation.js",
    "Prescription":         "public/js/prescription.js",
    "Lab Request":          "public/js/lab_request.js",
    "Radiology Request":    "public/js/radiology_request.js",
    "Pharmacy Dispensing":  "public/js/pharmacy_dispensing.js",
    "ICU Monitoring":       "public/js/icu_monitoring.js",
}

# ─────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────
notification_config = "hospital_portal.notifications.get_notification_config"
