import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. Locate the dataset
# --------------------------------------------------

DATA_PATH = Path(
    "data/raw/PDC_clinical_manifest_10032026_200348.csv"
)

# --------------------------------------------------
# 2. Load the CSV
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("CPTAC-PDA CLINICAL DATASET")
print("=" * 60)

print("\nDataset shape:")
print(df.shape)

print("\nNumber of patients/records:")
print(len(df))

# --------------------------------------------------
# 3. Show column names
# --------------------------------------------------

print("\nColumns:")
for i, column in enumerate(df.columns, start=1):
    print(f"{i:3}. {column}")

# --------------------------------------------------
# 4. Show first 5 rows
# --------------------------------------------------

print("\nFirst 5 rows:")
print(df.head())

# --------------------------------------------------
# 5. Show data types
# --------------------------------------------------

print("\nData types:")
print(df.dtypes)

# --------------------------------------------------
# 6. Missing values
# --------------------------------------------------

missing = pd.DataFrame({
    "missing_count": df.isna().sum(),
    "missing_percentage": df.isna().mean() * 100
})

missing = missing.sort_values(
    "missing_percentage",
    ascending=False
)

print("\nMissing values:")
print(missing.head(30))

# --------------------------------------------------
# 7. Important clinical variables
# --------------------------------------------------

important_columns = [
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
    "Lymphatic Invasion Present",
    "Perineural Invasion Present",
    "Vascular Invasion Present",
    "Margins Involved Site",
    "Overall Survival",
    "Days to Death",
    "Days to Last Follow Up",
    "Vital Status",
]

print("\nImportant columns:")
print(df[important_columns].head(10))

# --------------------------------------------------
# 8. Survival status
# --------------------------------------------------

print("\nVital Status values:")
print(df["Vital Status"].value_counts(dropna=False))

print("\nDone.")