"""
FAERS GLP-1 cleaning pipeline (owner: Rutu).

The notebook notebooks/01_data_cleaning.ipynb calls these functions one step
at a time. Each function does ONE job, so each step can be explained and
checked on its own.

Memory note: one FAERS quarter has millions of DRUG and REAC rows, so we
process ONE QUARTER AT A TIME and keep only GLP-1 reports from each quarter.
"""
import csv
import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from src.definitions import (
    AGE_BINS, AGE_LABELS, AGE_MAX, AGE_MIN, AGE_TO_YEARS, BRANDS,
    EXCLUDE_KEYWORDS, GLP1_KEYWORDS, HCP_CODES, REPORTER_TYPES,
    SERIOUS_CODES, UNKNOWN_INDICATIONS, WEIGHT_MAX, WEIGHT_MIN, WEIGHT_TO_KG,
    WEIGHT_WORDS,
)

# Run settings (delimiter, encoding) come from config.yml, like ingest.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CONFIG = yaml.safe_load((PROJECT_ROOT / "config.yml").read_text())
DELIMITER = _CONFIG["ingestion"]["delimiter"]
ENCODING = _CONFIG["ingestion"]["encoding"]

TABLES = ["DEMO", "DRUG", "REAC", "OUTC", "INDI"]
FILE_PATTERN = re.compile(r"^(DEMO|DRUG|REAC|OUTC|INDI)(\d{2})Q(\d)\.TXT$",
                          re.IGNORECASE)
DELETED_PATTERN = re.compile(r"^DELE.*\.TXT$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Step 1: find the files
# ---------------------------------------------------------------------------
def find_quarter_files(raw_dir):
    """Search data/01_raw (any folder layout) and group the files by quarter.

    Returns {"2025Q1": {"DEMO": path, "DRUG": path, ...}, ...}
    """
    quarters = {}
    for path in Path(raw_dir).rglob("*"):
        match = FILE_PATTERN.match(path.name)
        if match:
            table, yy, q = match.groups()
            key = f"20{yy}Q{q}"
            quarters.setdefault(key, {})[table.upper()] = path
    return dict(sorted(quarters.items()))


def find_deleted_files(raw_dir):
    """Recent FAERS zips include a 'Deleted' file listing removed case ids."""
    return [p for p in Path(raw_dir).rglob("*") if DELETED_PATTERN.match(p.name)]


def read_faers(path, usecols=None):
    """Read one $-separated FAERS file as text columns (lower-case names).

    usecols: only these columns are loaded (saves memory on DRUG and REAC).
    """
    wanted = None
    if usecols:
        names = {c.lower() for c in usecols} | ({"outc_code"} if "outc_cod" in usecols else set())
        wanted = lambda col: col.strip().lower() in names
    df = pd.read_csv(path, sep=DELIMITER, encoding=ENCODING, dtype=str,
                     quoting=csv.QUOTE_NONE, on_bad_lines="skip",
                     low_memory=False, usecols=wanted)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.loc[:, ~df.columns.str.startswith("unnamed")]   # trailing $
    if "outc_code" in df.columns:                           # 2012Q4 spelling
        df = df.rename(columns={"outc_code": "outc_cod"})
    if usecols:
        df = df[[c for c in usecols if c in df.columns]]
    return df


def read_deleted_caseids(paths):
    """Collect every case id listed in the 'Deleted' files."""
    ids = set()
    for p in paths:
        text = Path(p).read_text(encoding=ENCODING, errors="ignore")
        ids.update(int(x) for x in re.findall(r"\b\d+\b", text))
    return ids


# ---------------------------------------------------------------------------
# Step 2: identify GLP-1 drugs
# ---------------------------------------------------------------------------
def map_glp1(prod_ai, drugname):
    """Return the GLP-1 ingredient name for one DRUG row, or None."""
    ai = str(prod_ai).upper() if pd.notna(prod_ai) else ""
    name = str(drugname).upper() if pd.notna(drugname) else ""
    if any(k in ai or k in name for k in EXCLUDE_KEYWORDS):
        return None
    for text in (ai, name):
        for keyword, drug in GLP1_KEYWORDS.items():
            if keyword in text:
                return drug
    return None


def map_brand(drugname):
    name = str(drugname).upper() if pd.notna(drugname) else ""
    for brand in BRANDS:
        if brand in name:
            return brand.title()
    return "Generic/other"


# ---------------------------------------------------------------------------
# Step 3: process ONE quarter -> GLP-1 reports, reactions, light DEMO
# ---------------------------------------------------------------------------
def process_quarter(quarter, files):
    """Return (reports, reactions, demo_light, counts) for one quarter."""
    counts = {"quarter": quarter}

    # --- DEMO (all reports, kept light for de-duplication later) ---
    demo = read_faers(files["DEMO"])
    counts["raw_reports"] = len(demo)
    demo = demo.drop_duplicates("primaryid", keep="last")   # repeated rows
    # Light copy for de-duplication: numbers take far less memory than text
    demo_light = pd.DataFrame({
        "primaryid": demo["primaryid"],
        "caseid": pd.to_numeric(demo["caseid"], errors="coerce"),
        "caseversion": pd.to_numeric(demo["caseversion"], errors="coerce"),
    })

    # --- DRUG: find GLP-1 rows ---
    drug = read_faers(files["DRUG"], usecols=[
        "primaryid", "drug_seq", "role_cod", "drugname", "prod_ai", "route",
        "dose_amt", "dose_unit", "dose_form"])
    n_drugs = drug.groupby("primaryid").size().rename("n_drugs")

    # Only rows that mention a GLP-1 keyword get the slower row-by-row mapping
    pattern = "|".join(GLP1_KEYWORDS)
    text = (drug["prod_ai"].fillna("") + " " + drug["drugname"].fillna("")).str.upper()
    cand = drug[text.str.contains(pattern, regex=True)].copy()
    cand["drug"] = [map_glp1(a, n) for a, n in zip(cand["prod_ai"], cand["drugname"])]
    cand = cand[cand["drug"].notna()]
    counts["glp1_mentioned_reports"] = cand["primaryid"].nunique()
    counts["glp1_mentioned_ids"] = set(cand["primaryid"])

    # Keep the GLP-1 as PRIMARY SUSPECT only; one row per report
    ps = cand[cand["role_cod"].str.upper() == "PS"].copy()
    ps["drug_seq_num"] = pd.to_numeric(ps["drug_seq"], errors="coerce")
    ps = ps.sort_values(["primaryid", "drug_seq_num"]).drop_duplicates("primaryid")
    counts["glp1_ps_reports"] = len(ps)
    ids = set(ps["primaryid"])
    del drug, text  # free memory before the next tables

    ps["brand"] = ps["drugname"].map(map_brand)
    ps["is_compounded"] = ps["drugname"].fillna("").str.upper().str.contains(
        "COMPOUND").astype(int)

    # --- DEMO details for GLP-1 reports ---
    keep = ["primaryid", "caseid", "caseversion", "age", "age_cod", "sex",
            "wt", "wt_cod", "occp_cod", "reporter_country", "rept_cod",
            "event_dt", "fda_dt"]
    d = demo[demo["primaryid"].isin(ids)]
    d = d[[c for c in keep if c in d.columns]]

    # --- OUTC: outcome flags ---
    outc = read_faers(files["OUTC"], ["primaryid", "outc_cod"])
    outc = outc[outc["primaryid"].isin(ids)]
    outc_flags = (outc.assign(v=1)
                  .pivot_table(index="primaryid", columns="outc_cod",
                               values="v", aggfunc="max", fill_value=0))

    # --- REAC: reactions (long table) ---
    reac = read_faers(files["REAC"], ["primaryid", "pt"])
    reac = reac[reac["primaryid"].isin(ids)].dropna(subset=["pt"])
    reac["pt"] = reac["pt"].str.strip().str.upper()
    reac = reac.drop_duplicates()
    n_reac = reac.groupby("primaryid").size().rename("n_reactions")

    # --- INDI: indication for the GLP-1 drug itself ---
    indi = read_faers(files["INDI"], ["primaryid", "indi_drug_seq", "indi_pt"])
    indi = indi.merge(ps[["primaryid", "drug_seq"]],
                      left_on=["primaryid", "indi_drug_seq"],
                      right_on=["primaryid", "drug_seq"], how="inner")
    indi_group = indi.groupby("primaryid")["indi_pt"].apply(group_indication)

    # --- Join everything into one row per report ---
    rep = (ps.drop(columns=["drug_seq_num"])
           .merge(d, on="primaryid", how="left")
           .merge(n_drugs, left_on="primaryid", right_index=True, how="left")
           .merge(n_reac, left_on="primaryid", right_index=True, how="left")
           .merge(indi_group.rename("indication_group"),
                  left_on="primaryid", right_index=True, how="left")
           .merge(outc_flags, left_on="primaryid", right_index=True, how="left"))
    rep["year_quarter"] = quarter
    reac["quarter"] = quarter
    return rep, reac, demo_light, counts


def group_indication(values):
    """Many indications for one drug -> one group (priority order)."""
    texts = [str(v).upper() for v in values if pd.notna(v)]
    texts = [t for t in texts if t not in UNKNOWN_INDICATIONS]
    if not texts:
        return "Unknown"
    if any("DIABETES" in t for t in texts):
        return "Diabetes"
    if any(w in t for t in texts for w in WEIGHT_WORDS):
        return "Weight loss"
    return "Other"


# ---------------------------------------------------------------------------
# Step 4: remove duplicate case versions (across ALL quarters)
# ---------------------------------------------------------------------------
def latest_primaryids(demo_light, deleted_caseids=()):
    """For each caseid keep the report with the highest caseversion.

    Returns the set of primaryids to keep and the number of unique cases.
    """
    d = demo_light.copy()
    d["caseid_n"] = pd.to_numeric(d["caseid"], errors="coerce")
    d["caseversion_n"] = pd.to_numeric(d["caseversion"], errors="coerce").fillna(0)
    d["primaryid_n"] = pd.to_numeric(d["primaryid"], errors="coerce")
    d = d[~d["caseid_n"].isin(set(deleted_caseids))]
    d = d.sort_values(["caseid_n", "caseversion_n", "primaryid_n"])
    latest = d.drop_duplicates("caseid_n", keep="last")
    return set(latest["primaryid"]), len(latest)


# ---------------------------------------------------------------------------
# Step 5: clean the columns
# ---------------------------------------------------------------------------
def clean_reports(rep):
    r = rep.copy()

    # Time
    r["year"] = r["year_quarter"].str[:4].astype(int)
    r["quarter"] = r["year_quarter"].str[-1].astype(int)

    # Age -> years (keep the raw values for the before/after chart)
    r["age_raw"] = pd.to_numeric(r["age"], errors="coerce")
    factor = r["age_cod"].str.upper().map(AGE_TO_YEARS)
    r["age_years"] = (r["age_raw"] * factor).round(1)
    r.loc[~r["age_years"].between(AGE_MIN, AGE_MAX), "age_years"] = np.nan
    r["age_group"] = (pd.cut(r["age_years"], bins=AGE_BINS, labels=AGE_LABELS,
                             right=False)
                      .cat.add_categories("Unknown").fillna("Unknown")
                      .astype(str))

    # Weight -> kg
    wt = pd.to_numeric(r["wt"], errors="coerce")
    r["weight_kg"] = (wt * r["wt_cod"].str.upper().map(WEIGHT_TO_KG)).round(1)
    r.loc[~r["weight_kg"].between(WEIGHT_MIN, WEIGHT_MAX), "weight_kg"] = np.nan

    # Sex
    r["sex"] = r["sex"].str.upper().where(r["sex"].str.upper().isin(["M", "F"]),
                                          "Unknown")

    # Reporter
    occ = r["occp_cod"].str.upper()
    r["reporter_type"] = occ.map(REPORTER_TYPES).fillna("Unknown")
    r["is_hcp"] = occ.isin(HCP_CODES).astype(int)
    r["reporter_country"] = r["reporter_country"].fillna("Unknown")

    # Counts
    r["n_reactions"] = r["n_reactions"].fillna(0).astype(int)
    r["n_other_drugs"] = (r["n_drugs"].fillna(1) - 1).clip(lower=0).astype(int)
    r["indication_group"] = r["indication_group"].fillna("Unknown")

    # Dose
    r["dose_amt"] = pd.to_numeric(r["dose_amt"], errors="coerce")

    # Outcomes
    for code in ["DE", "LT", "HO", "DS", "CA", "RI", "OT"]:
        if code not in r.columns:
            r[code] = 0
        r[code] = r[code].fillna(0).astype(int)
    r["is_death"] = r["DE"]
    r["is_life_threatening"] = r["LT"]
    r["is_hospitalized"] = r["HO"]
    r["is_disability"] = r["DS"]
    r["is_serious"] = (r[SERIOUS_CODES].max(axis=1) > 0).astype(int)

    columns = [
        "primaryid", "caseid", "year", "quarter", "year_quarter",
        "drug", "brand", "is_compounded", "drugname", "prod_ai",
        "route", "dose_amt", "dose_unit", "dose_form",
        "age_raw", "age_cod", "age_years", "age_group", "weight_kg", "sex",
        "reporter_type", "is_hcp", "reporter_country", "indication_group",
        "n_reactions", "n_other_drugs",
        "is_death", "is_life_threatening", "is_hospitalized", "is_disability",
        "is_serious",
    ]
    return r[[c for c in columns if c in r.columns]]
