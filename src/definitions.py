"""
Shared definitions for the DATA 230 Group 4 project (FAERS GLP-1).

Every notebook imports from this file so that everyone uses the SAME rules:
    from src.definitions import *

Do not copy these lists into your own notebook. If a rule needs to change,
change it here (in a pull request) and tell the team.
"""

# ---------------------------------------------------------------------------
# 1. Reading the raw FAERS files
# ---------------------------------------------------------------------------
DELIMITER = "$"          # FAERS ASCII files are separated by $
ENCODING = "latin-1"     # never fails on special characters (é, ñ, ...)

# ---------------------------------------------------------------------------
# 2. GLP-1 drugs: keyword -> standard ingredient name
#    Matched (upper case) against prod_ai first, then drugname.
# ---------------------------------------------------------------------------
GLP1_KEYWORDS = {
    "SEMAGLUTIDE": "semaglutide", "OZEMPIC": "semaglutide",
    "WEGOVY": "semaglutide", "RYBELSUS": "semaglutide",
    "TIRZEPATIDE": "tirzepatide", "MOUNJARO": "tirzepatide",
    "ZEPBOUND": "tirzepatide",
    "DULAGLUTIDE": "dulaglutide", "TRULICITY": "dulaglutide",
    "LIRAGLUTIDE": "liraglutide", "VICTOZA": "liraglutide",
    "SAXENDA": "liraglutide",
}

# Brand names, used for the `brand` column (dashboard filter)
BRANDS = ["OZEMPIC", "WEGOVY", "RYBELSUS", "MOUNJARO", "ZEPBOUND",
          "TRULICITY", "VICTOZA", "SAXENDA"]

# Combination products we leave out (insulin + GLP-1)
EXCLUDE_KEYWORDS = ["XULTOPHY", "SOLIQUA", "INSULIN"]

GLP1_DRUGS = ["semaglutide", "tirzepatide", "dulaglutide", "liraglutide"]

# ---------------------------------------------------------------------------
# 3. Outcomes: what counts as a "serious" report (the ML target)
# ---------------------------------------------------------------------------
SERIOUS_CODES = ["DE", "LT", "HO", "DS", "CA", "RI"]
OUTCOME_NAMES = {
    "DE": "Death", "LT": "Life-threatening", "HO": "Hospitalization",
    "DS": "Disability", "CA": "Congenital anomaly",
    "RI": "Required intervention", "OT": "Other serious",
}

# ---------------------------------------------------------------------------
# 4. Age and weight conversions
# ---------------------------------------------------------------------------
AGE_TO_YEARS = {"YR": 1.0, "DEC": 10.0, "MON": 1 / 12, "WK": 1 / 52.18,
                "DY": 1 / 365.25, "HR": 1 / 8766}
AGE_MIN, AGE_MAX = 0, 110

AGE_BINS = [0, 18, 40, 65, 200]
AGE_LABELS = ["Under 18", "18-39", "40-64", "65 and over"]

WEIGHT_TO_KG = {"KG": 1.0, "LBS": 0.4536, "LB": 0.4536}
WEIGHT_MIN, WEIGHT_MAX = 30, 300

# ---------------------------------------------------------------------------
# 5. Reporter type (occp_cod)
# ---------------------------------------------------------------------------
REPORTER_TYPES = {
    "MD": "Physician", "PH": "Pharmacist", "OT": "Other health professional",
    "HP": "Health professional", "LW": "Lawyer", "CN": "Consumer",
}
HCP_CODES = ["MD", "PH", "OT", "HP"]

# ---------------------------------------------------------------------------
# 6. Indication groups (why the drug was taken)
# ---------------------------------------------------------------------------
UNKNOWN_INDICATIONS = ["PRODUCT USED FOR UNKNOWN INDICATION",
                       "DRUG USE FOR UNKNOWN INDICATION"]
WEIGHT_WORDS = ["WEIGHT", "OBES", "OVERWEIGHT"]

# ---------------------------------------------------------------------------
# 7. Fixed drug colors (same in Python and Tableau)
# ---------------------------------------------------------------------------
DRUG_COLORS = {
    "semaglutide": "#2563EB",   # blue
    "tirzepatide": "#DC2626",   # red
    "dulaglutide": "#059669",   # green
    "liraglutide": "#D97706",   # orange
}
