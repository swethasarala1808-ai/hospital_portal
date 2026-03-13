"""
🔐 Medicare Hospital - Portal Access Guard
==========================================
INSTRUCTIONS:
  Copy the has_website_permission() function below into your
  hospital_portal/permissions.py file.

  Then in your hooks.py, make sure this is set:
    has_website_permission = "hospital_portal.permissions.has_website_permission"

This ensures each department user is redirected to their portal ONLY,
and cannot manually navigate to another department's portal URL.
"""

# ─────────────────────────────────────────────
# ADD THIS TO: hospital_portal/permissions.py
# ─────────────────────────────────────────────

PORTAL_ROLE_MAP = {
    "/registration-portal": ["Registration Staff", "Hospital Head", "Administrator"],
    "/nurse-portal":        ["Nurse", "Hospital Head", "Administrator"],
    "/doctor-portal":       ["Doctor", "Hospital Head", "Administrator"],
    "/lab-portal":          ["Lab Technician", "Pathologist", "Hospital Head", "Administrator"],
    "/radiology-portal":    ["Radiographer", "Radiologist", "Hospital Head", "Administrator"],
    "/pharmacy-portal":     ["Pharmacist", "Hospital Head", "Administrator"],
    "/ipd-portal":          ["Ward Nurse", "Hospital Head", "Administrator"],
    "/icu-portal":          ["ICU Nurse", "Intensivist", "Hospital Head", "Administrator"],
    "/hospital-dashboard":  ["Hospital Head", "Administrator"],
    "/patient-portal":      ["Patient", "Hospital Head", "Administrator"],
}

# User → default portal redirect
ROLE_DEFAULT_PORTAL = {
    "Registration Staff": "/registration-portal",
    "Nurse":              "/nurse-portal",
    "Doctor":             "/doctor-portal",
    "Lab Technician":     "/lab-portal",
    "Pathologist":        "/lab-portal",
    "Radiographer":       "/radiology-portal",
    "Radiologist":        "/radiology-portal",
    "Pharmacist":         "/pharmacy-portal",
    "Ward Nurse":         "/ipd-portal",
    "ICU Nurse":          "/icu-portal",
    "Intensivist":        "/icu-portal",
    "Hospital Head":      "/hospital-dashboard",
}


def has_website_permission(doc, ptype, user, verbose=False):
    """
    Called by Frappe's website permission check.
    Returns True if user is allowed to access the page.
    """
    import frappe as _frappe

    if user in ("Administrator", "Guest"):
        return True

    user_roles = _frappe.get_roles(user)

    # Allow Hospital Head and Administrator everywhere
    if "Hospital Head" in user_roles or "Administrator" in user_roles:
        return True

    # Get current page path (passed via doc.name for web pages)
    page_path = f"/{doc.name}" if hasattr(doc, "name") else ""

    allowed_roles_for_page = PORTAL_ROLE_MAP.get(page_path, [])

    for role in user_roles:
        if role in allowed_roles_for_page:
            return True

    return False


def get_user_default_portal(user=None):
    """Returns the default portal URL for a given user based on their role."""
    import frappe as _frappe

    if not user:
        user = _frappe.session.user

    user_roles = _frappe.get_roles(user)

    for role, portal in ROLE_DEFAULT_PORTAL.items():
        if role in user_roles:
            return portal

    return "/hospital-dashboard"


# ─────────────────────────────────────────────
# ADD THIS TO: hospital_portal/www/*.html (top of each portal page)
# ─────────────────────────────────────────────

PORTAL_ACCESS_GUARD_JS = """
<!-- Add this script block at the top of each portal page HTML -->
<script>
// Portal Access Guard
// Redirect unauthorized users away from this page

const PORTAL_ROLE_MAP = {
  "/registration-portal": ["Registration Staff", "Hospital Head", "Administrator"],
  "/nurse-portal":        ["Nurse", "Hospital Head", "Administrator"],
  "/doctor-portal":       ["Doctor", "Hospital Head", "Administrator"],
  "/lab-portal":          ["Lab Technician", "Pathologist", "Hospital Head", "Administrator"],
  "/radiology-portal":    ["Radiographer", "Radiologist", "Hospital Head", "Administrator"],
  "/pharmacy-portal":     ["Pharmacist", "Hospital Head", "Administrator"],
  "/ipd-portal":          ["Ward Nurse", "Hospital Head", "Administrator"],
  "/icu-portal":          ["ICU Nurse", "Intensivist", "Hospital Head", "Administrator"],
  "/hospital-dashboard":  ["Hospital Head", "Administrator"],
};

const ROLE_PORTAL_MAP = {
  "Registration Staff": "/registration-portal",
  "Nurse":              "/nurse-portal",
  "Doctor":             "/doctor-portal",
  "Lab Technician":     "/lab-portal",
  "Pathologist":        "/lab-portal",
  "Radiographer":       "/radiology-portal",
  "Radiologist":        "/radiology-portal",
  "Pharmacist":         "/pharmacy-portal",
  "Ward Nurse":         "/ipd-portal",
  "ICU Nurse":          "/icu-portal",
  "Intensivist":        "/icu-portal",
  "Hospital Head":      "/hospital-dashboard",
};

function checkPortalAccess() {
  frappe.call({
    method: "frappe.client.get_value",
    args: { doctype: "User", filters: { name: frappe.session.user }, fieldname: ["full_name"] },
    callback: function() {
      // Get user roles
      frappe.call({
        method: "frappe.boot.get_boot_info",
        callback: function(r) {
          // Use session user roles
        }
      });
    }
  });

  // Simpler: use frappe.user_roles if available
  const currentPath = window.location.pathname;
  const userRoles = frappe.user_roles || [];

  if (userRoles.includes("Administrator") || userRoles.includes("Hospital Head")) {
    return; // Allow full access
  }

  const allowedRoles = PORTAL_ROLE_MAP[currentPath] || [];
  const hasAccess = userRoles.some(r => allowedRoles.includes(r));

  if (!hasAccess && frappe.session.user !== "Guest") {
    // Find user's correct portal
    for (const [role, portal] of Object.entries(ROLE_PORTAL_MAP)) {
      if (userRoles.includes(role)) {
        window.location.href = portal;
        return;
      }
    }
    window.location.href = "/login";
  }
}

$(document).ready(function() {
  if (frappe && frappe.session && frappe.session.user !== "Guest") {
    checkPortalAccess();
  }
});
</script>
"""


# ─────────────────────────────────────────────
# HOOKS.PY additions (add these lines to your hooks.py)
# ─────────────────────────────────────────────

HOOKS_ADDITIONS = """
# ─── Add these to hospital_portal/hooks.py ───

# Role-based portal redirect on login
role_home_page = {
    "Registration Staff": "registration-portal",
    "Nurse":              "nurse-portal",
    "Doctor":             "doctor-portal",
    "Lab Technician":     "lab-portal",
    "Pathologist":        "lab-portal",
    "Radiographer":       "radiology-portal",
    "Radiologist":        "radiology-portal",
    "Pharmacist":         "pharmacy-portal",
    "Ward Nurse":         "ipd-portal",
    "ICU Nurse":          "icu-portal",
    "Intensivist":        "icu-portal",
    "Hospital Head":      "hospital-dashboard",
}

# Website permissions
has_website_permission = {
    "Patient Registration": "hospital_portal.permissions.has_website_permission",
    "Appointment":          "hospital_portal.permissions.has_website_permission",
    "Vital Signs":          "hospital_portal.permissions.has_website_permission",
    "Consultation":         "hospital_portal.permissions.has_website_permission",
    "Prescription":         "hospital_portal.permissions.has_website_permission",
    "Lab Request":          "hospital_portal.permissions.has_website_permission",
    "Lab Report":           "hospital_portal.permissions.has_website_permission",
    "Radiology Request":    "hospital_portal.permissions.has_website_permission",
    "Radiology Report":     "hospital_portal.permissions.has_website_permission",
    "Pharmacy Dispensing":  "hospital_portal.permissions.has_website_permission",
    "IPD Admission":        "hospital_portal.permissions.has_website_permission",
    "ICU Monitoring":       "hospital_portal.permissions.has_website_permission",
}
"""

print(__doc__)
print("\n📋 Copy HOOKS_ADDITIONS to your hooks.py:")
print(HOOKS_ADDITIONS)
