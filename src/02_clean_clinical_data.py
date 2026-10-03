import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

INPUT_PATH = Path(
    "data/raw/PDC_clinical_manifest_10032026_200348.csv"
)

OUTPUT_PATH = Path(
    "data/processed/clinical_survival_clean.csv"
)

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_PATH)

print("Original dataset:")
print(df.shape)

# ============================================================
# STANDARDIZE EMPTY VALUES
# ============================================================

# Convert blank strings and common "missing" labels to NaN
missing_values = [
    "",
    " ",
    "Not Reported",
    "Unknown",
    "not reported",
    "unknown"
]

df = df.replace(missing_values, np.nan)

# ============================================================
# SELECT CLINICAL VARIABLES
# ============================================================

columns_to_keep = [
    "Case Submitter ID",
    "Sex",
    "Race",
    "Ethnicity",
    "Age at Diagnosis",
    "Tumor Grade",
    "AJCC Pathologic Stage",
    "AJCC Pathologic T",
    "AJCC Pathologic N",
    "AJCC Pathologic M",
    "Lymph Nodes Positive",
    "Lymph Nodes Tested",
    "Metastasis At Diagnosis",
    "Metastasis At Diagnosis Site",
    "Lymphatic Invasion Present",
    "Perineural Invasion Present",
    "Vascular Invasion Present",
    "Vascular Invasion Type",
    "Margins Involved Site",
    "Tumor Regression Grade",
    "Days to Death",
    "Days to Last Follow Up",
    "Vital Status",
]

df = df[columns_to_keep].copy()

# ============================================================
# CLEAN PATIENT ID
# ============================================================

df["Case Submitter ID"] = (
    df["Case Submitter ID"]
    .astype(str)
    .str.strip()
)

# ============================================================
# CONVERT AGE FROM DAYS TO YEARS
# ============================================================

df["Age at Diagnosis"] = pd.to_numeric(
    df["Age at Diagnosis"],
    errors="coerce"
)

df["Age_years"] = (
    df["Age at Diagnosis"] / 365.25
)

# ============================================================
# CONVERT SURVIVAL VARIABLES TO NUMERIC
# ============================================================

df["Days to Death"] = pd.to_numeric(
    df["Days to Death"],
    errors="coerce"
)

df["Days to Last Follow Up"] = pd.to_numeric(
    df["Days to Last Follow Up"],
    errors="coerce"
)

# ============================================================
# CREATE SURVIVAL EVENT
# ============================================================

df["survival_event"] = np.nan

df.loc[
    df["Vital Status"].str.lower() == "dead",
    "survival_event"
] = 1

df.loc[
    df["Vital Status"].str.lower() == "alive",
    "survival_event"
] = 0

# ============================================================
# CREATE SURVIVAL TIME
# ============================================================

# If dead:
# use Days to Death
#
# If alive:
# use Days to Last Follow Up

df["survival_time_days"] = np.where(
    df["survival_event"] == 1,
    df["Days to Death"],
    df["Days to Last Follow Up"]
)

# ============================================================
# REMOVE PATIENTS WITHOUT USABLE SURVIVAL INFORMATION
# ============================================================

before = len(df)

df = df.dropna(
    subset=[
        "survival_event",
        "survival_time_days"
    ]
)

after = len(df)

print("\nPatients before survival filtering:", before)
print("Patients after survival filtering:", after)
print("Patients removed:", before - after)

# ============================================================
# REMOVE IMPOSSIBLE SURVIVAL TIMES
# ============================================================

df = df[
    df["survival_time_days"] >= 0
].copy()

# ============================================================
# CONVERT SURVIVAL TIME TO MONTHS
# ============================================================

df["survival_time_months"] = (
    df["survival_time_days"] / 30.44
)

# ============================================================
# CHECK THE RESULT
# ============================================================

print("\nFinal dataset shape:")
print(df.shape)

print("\nSurvival event:")
print(df["survival_event"].value_counts())

print("\nClinical dataset preview:")
print(
    df[
        [
            "Case Submitter ID",
            "Age_years",
            "Sex",
            "Tumor Grade",
            "AJCC Pathologic Stage",
            "survival_time_days",
            "survival_event"
        ]
    ].head(10)
)

# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nSaved cleaned dataset to:")
print(OUTPUT_PATH)