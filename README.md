# Pancreatic Cancer Prognosis Using Clinical and Radiomic Data

UE24CS352A Machine Learning mini-project. We re-implement the survival-analysis pipeline of *"Pancreatic cancer prognosis using clinical and radiomic data"* (CS229 final report, A. Jamalian, 2020) using the public **CPTAC-PDA** dataset from The Cancer Imaging Archive (TCIA).

**Team:**

- PES2UG24CS288 Muralikrishnan Menon
- PES2UG24CS300 Namitha Ravikumar

## Problem

Predict survival of pancreatic ductal adenocarcinoma (PDAC) patients using **clinical and radiomic features** and measure the additional prognostic value obtained by combining both feature sets.

The project uses CT/MR imaging to extract quantitative radiomic features from annotated pancreatic tumors. Clinical variables and survival information are then combined with the radiomic features for survival analysis.

Models are evaluated using the concordance index (C-index). Patients can also be separated into high- and low-risk groups and evaluated using Kaplan-Meier curves and a log-rank test.

## Dataset

### CPTAC-PDA

**Clinical Proteomic Tumor Analysis Consortium Pancreatic Ductal Adenocarcinoma Collection (CPTAC-PDA)**

Source: **The Cancer Imaging Archive (TCIA)**

Dataset page:
https://www.cancerimagingarchive.net/collection/cptac-pda/

CPTAC-PDA is a public pancreatic ductal adenocarcinoma dataset containing radiology images together with linked clinical, genomic and proteomic resources. The current TCIA release contains 168 subjects overall and 110 subjects with radiology images. The radiology data contains CT, MR, US and PT images in DICOM format.

For this project, we focus on the **CT/MR radiology images**, the linked clinical data, and the public tumor annotations.

### Tumor annotations

The CPTAC-PDA Tumor Annotations analysis result provides tumor segmentations for **103 subjects**.

Source:
https://www.cancerimagingarchive.net/analysis-result/cptac-pda-tumor-annotations/

These annotations are used to define the region of interest (ROI) from which radiomic features are extracted.

### Data blocks

| Block | Source | Used for |
|---|---|---|
| Radiology | CPTAC-PDA / TCIA | CT/MR images |
| Tumor ROI | CPTAC-PDA Tumor Annotations | Tumor segmentation |
| Radiomics | Extracted with PyRadiomics | First-order, shape, texture and other quantitative image features |
| Clinical | CPTAC clinical resources through PDC/GDC | Patient and tumor clinical variables |
| Survival | Linked CPTAC clinical data | Survival time and event/censoring status |

TCIA states that CPTAC subject identifiers are shared across TCIA imaging and the corresponding CPTAC clinical, genomic and proteomic resources, allowing the data sources to be linked at the patient level.


## Repository Structure

```text
pancreatic-cancer-prognosis/
│
├── data/
│   ├── raw/
│   │   ├── PDC_clinical_manifest_10032026_200348.csv
│   │   ├── PDC_clinical_exposure_manifest_10032026_200348.csv
│   │   ├── PDC_clinical_followup_manifest_10032026_200348.csv
│   │   └── PDC_clinical_treatment_manifest_10032026_200348.csv
│   │
│   └── processed/
│       └── clinical_survival_clean.csv
│
├── src/
│   ├── 01_inspect_data.py
│   ├── 02_clean_clinical_data.py
│   ├── 03_missing_data.py
│   ├── 04_eda.py
│   ├── 05_kaplan_meier.py
│   ├── 06_km_by_grade.py
│   └── 07_cox_model.py
│
├── results/
│   ├── missing_data_report.csv
│   ├── age_distribution.png
│   ├── sex_distribution.png
│   ├── tumor_grade_distribution.png
│   ├── survival_time_distribution.png
│   ├── kaplan_meier_overall_survival.png
│   ├── kaplan_meier_by_tumor_grade.png
│   └── cox_model_results.csv
│
├── requirements.txt
└── README.md
```


## Setup

Create and activate a Python virtual environment:

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Analysis Pipeline

Run the scripts in the following order:

### Inspect clinical data

```bash
python src/01_inspect_data.py
```

This step is used to inspect the downloaded clinical manifests, understand their columns and identify the variables required for subsequent analysis.

### Clean clinical data

```bash
python src/02_clean_clinical_data.py
```

This step cleans the relevant clinical variables and creates:

```text
data/processed/clinical_survival_clean.csv
```

### Analyse missing data

```bash
python src/03_missing_data.py
```

Output:

```text
results/missing_data_report.csv
```

### Exploratory data analysis

```bash
python src/04_eda.py
```

Expected plots:

```text
results/age_distribution.png
results/sex_distribution.png
results/tumor_grade_distribution.png
results/survival_time_distribution.png
```

### Overall Kaplan-Meier analysis

```bash
python src/05_kaplan_meier.py
```

Output:

```text
results/kaplan_meier_overall_survival.png
```

### Kaplan-Meier analysis by tumor grade

```bash
python src/06_km_by_grade.py
```

Output:

```text
results/kaplan_meier_by_tumor_grade.png
```

### Cox proportional hazards model

```bash
python src/07_cox_model.py
```

Output:

```text
results/cox_model_results.csv
```

## Survival Analysis

### Survival endpoint

The cleaned dataset contains the variables required for survival analysis:

- `duration` — survival/follow-up time.
- `event` — event indicator.
- `event = 1` — observed death/event.
- `event = 0` — right-censored case.

The exact clinical variable names and transformations are determined from the downloaded CPTAC-PDA clinical manifests during the cleaning step.

### Kaplan-Meier analysis

Kaplan-Meier analysis is used to estimate overall survival over time.

The project also compares survival between tumor-grade groups where sufficient data is available.

### Cox proportional hazards model

A Cox proportional hazards model is used to investigate the relationship between clinical variables and survival.

The model produces coefficient and hazard-ratio information for the selected clinical variables.

The resulting model information is saved in:

```text
results/cox_model_results.csv
```

## Results

The current clinical/survival analysis produces the following outputs:

```text
results/
├── missing_data_report.csv
├── age_distribution.png
├── sex_distribution.png
├── tumor_grade_distribution.png
├── survival_time_distribution.png
├── kaplan_meier_overall_survival.png
├── kaplan_meier_by_tumor_grade.png
└── cox_model_results.csv
```

Results and numerical findings should be updated here after the analysis scripts have been run on the final cleaned dataset.
