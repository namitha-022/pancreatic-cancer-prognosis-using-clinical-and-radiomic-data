from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CLINICAL_FILE = (
    PROJECT_ROOT / "data" / "processed" / "clinical_survival_clean.csv"
)

IMAGING_DIR = PROJECT_ROOT / "data" / "raw" / "imaging"

ANNOTATION_FILE = (
    IMAGING_DIR / "Metadata_Report_CPTAC_PDA_2025_10-20.csv"
)

# Change this filename if your second TCIA CSV has a different name.
IMAGING_METADATA_FILE = IMAGING_DIR / "imaging_metadata.csv"

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


# ============================================================
# HELPER
# ============================================================

def clean_id(series):
    """Clean patient IDs for reliable matching."""
    return (
        series.astype(str)
        .str.strip()
        .str.upper()
    )


# ============================================================
# LOAD CLINICAL DATA
# ============================================================

print("\n========== CLINICAL DATA ==========")

clinical = pd.read_csv(CLINICAL_FILE)

print("Clinical shape:", clinical.shape)
print("\nClinical columns:")
print(clinical.columns.tolist())

if "Case Submitter ID" not in clinical.columns:
    raise ValueError(
        "Could not find 'Case Submitter ID' in clinical_survival_clean.csv"
    )

clinical_ids = set(
    clean_id(clinical["Case Submitter ID"]).dropna()
)

print("\nUnique clinical patients:", len(clinical_ids))


# ============================================================
# LOAD ANNOTATION METADATA
# ============================================================

print("\n========== ANNOTATION DATA ==========")

annotation = pd.read_csv(ANNOTATION_FILE)

print("Annotation shape:", annotation.shape)

print("\nAnnotation columns:")
print(annotation.columns.tolist())

if "PatientID" not in annotation.columns:
    raise ValueError(
        "Could not find 'PatientID' in annotation metadata."
    )

annotation_ids = set(
    clean_id(annotation["PatientID"]).dropna()
)

print("\nUnique annotated patients:", len(annotation_ids))


# ============================================================
# CLINICAL + ANNOTATION OVERLAP
# ============================================================

clinical_annotation_ids = clinical_ids.intersection(annotation_ids)

print("\n========== CLINICAL + ANNOTATION ==========")

print(
    "Patients present in BOTH clinical and annotation data:",
    len(clinical_annotation_ids)
)


# ============================================================
# LOAD IMAGING METADATA
# ============================================================

print("\n========== IMAGING DATA ==========")

if not IMAGING_METADATA_FILE.exists():
    print(
        "\nWARNING:"
        "\nImaging metadata file was not found:"
        f"\n{IMAGING_METADATA_FILE}"
        "\n\nRename your imaging metadata CSV to:"
        "\nimaging_metadata.csv"
        "\nthen run this script again."
    )
    raise SystemExit

imaging = pd.read_csv(IMAGING_METADATA_FILE)

print("Imaging metadata shape:", imaging.shape)

print("\nImaging columns:")
print(imaging.columns.tolist())


# ============================================================
# FIND PATIENT ID COLUMN
# ============================================================

possible_patient_columns = [
    "PatientID",
    "Patient ID",
    "Subject ID",
    "SubjectID",
    "Case Submitter ID",
]

imaging_patient_column = None

for col in possible_patient_columns:
    if col in imaging.columns:
        imaging_patient_column = col
        break

if imaging_patient_column is None:
    raise ValueError(
        "Could not find a patient/subject ID column "
        "in the imaging metadata."
    )

print(
    "\nUsing imaging patient column:",
    imaging_patient_column
)

imaging_ids = set(
    clean_id(imaging[imaging_patient_column]).dropna()
)

print(
    "Unique imaging patients:",
    len(imaging_ids)
)


# ============================================================
# FINAL OVERLAP
# ============================================================

final_ids = (
    clinical_ids
    .intersection(annotation_ids)
    .intersection(imaging_ids)
)

print("\n========== FINAL OVERLAP ==========")

print(
    "Clinical patients:",
    len(clinical_ids)
)

print(
    "Annotated patients:",
    len(annotation_ids)
)

print(
    "Imaging patients:",
    len(imaging_ids)
)

print(
    "Clinical + annotation:",
    len(clinical_annotation_ids)
)

print(
    "Clinical + annotation + imaging:",
    len(final_ids)
)


# ============================================================
# SAVE MATCHING PATIENTS
# ============================================================

mapping = pd.DataFrame({
    "PatientID": sorted(final_ids)
})

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "radiomics_patient_ids.csv"

mapping.to_csv(output_file, index=False)

print("\nSaved:", output_file)

print("\nFirst matching patients:")

print(
    mapping.head(20).to_string(index=False)
)

print("\n========== DONE ==========\n")
