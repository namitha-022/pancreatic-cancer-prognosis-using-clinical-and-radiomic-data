# Pancreatic Cancer Prognosis Using Clinical and Radiomic Data

UE24CS352A Machine Learning mini-project. We re-implement the survival-analysis pipeline of *"Pancreatic cancer prognosis using clinical and radiomic data"* (CS229 final report, A. Jamalian, 2020) using the public **CPTAC-PDA** dataset from The Cancer Imaging Archive (TCIA).

**Team:**

- PES2UG24CS288 Muralikrishnan Menon
- PES2UG24CS300 Namitha Ravikumar

## Problem

Predict survival of pancreatic ductal adenocarcinoma (PDAC) patients using **clinical and radiomic features** and measure the additional prognostic value obtained by combining both feature sets.

The project uses CT/MR imaging to extract quantitative radiomic features from annotated pancreatic tumors. Clinical variables and survival information are then combined with the radiomic features for survival analysis.

Models are evaluated using the concordance index (C-index). Patients can also be separated into high- and low-risk groups and evaluated using Kaplan-Meier curves and a log-rank test.

## Reproducibility status

The committed processed clinical cohort contains **144** patients with usable
survival data (115 events and 29 censored observations). The clinical pipeline
has been run successfully on that cohort. The clinical-only penalised Cox model
uses 143 positive-duration records and has an apparent C-index of 0.680; it is
exploratory, not external validation. The threshold classifier is also
exploratory (held-out balanced accuracy 0.417), so it must not be used for
clinical decision-making.

The repository does **not** contain the raw PDC manifest, images, annotations,
or a radiomics feature table. Accordingly, no radiomics or combined-model
performance is claimed. This is intentional: patient-level raw data and large
imaging files are excluded from version control. See
[`data/raw/README.md`](data/raw/README.md) for the exact expected inputs.

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

├── data/
│   ├── raw/
│   │   ├── PDC_clinical_manifest_10032026_200348.csv
│   │   ├── PDC_clinical_exposure_manifest_10032026_200348.csv
│   │   ├── PDC_clinical_followup_manifest_10032026_200348.csv
│   │   └── PDC_clinical_treatment_manifest_10032026_200348.csv
│   └─── processed/
│       ├── clinical_survival_clean.csv
│       └── clinical_preprocessed.csv
│
├── src/
│   ├── 01_inspect_data.py
│   ├── 02_clean_clinical_data.py
│   ├── 03_missing_data.py
│   ├── 04_eda.py
│   ├── 05_kaplan_meier.py
│   ├── 06_km_by_grade.py
│   ├── 07_cox_model.py
│   ├── 08_preprocess_clinical.py
│   ├── 09_naive_bayes_threshold.py
│   ├── 10_smote_classification.py
│   ├── 11_cox_full_analysis.py
│   ├── 12_logrank_analysis.py
│   ├── 13_cox_risk_km.py
│   └── 14_final_results_table.py
│
├── results/
│   ├── missing_data_report.csv
│   ├── removed_clinical_features.csv
│   ├── naive_bayes_threshold_results.csv
│   ├── smote_classification_results.csv
│   ├── smote_class_distribution.csv
│   ├── cox_full_results.csv
│   ├── clinical_model_summary.csv
│   ├── cox_proportional_hazards_test.csv
│   ├── cox_removed_features.csv
│   ├── logrank_threshold_results.csv
│   ├── cox_risk_groups.csv
│   ├── cox_risk_logrank_results.csv
│   ├── final_clinical_results.csv
│   ├── final_clinical_model_summary.csv
│   ├── age_distribution.png
│   ├── sex_distribution.png
│   ├── tumor_grade_distribution.png
│   ├── survival_time_distribution.png
│   ├── kaplan_meier_overall_survival.png
│   ├── kaplan_meier_by_tumor_grade.png
│   ├── kaplan_meier_by_survival_threshold.png
│   └── kaplan_meier_cox_risk_groups.png
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

## Run the validated clinical analysis

The processed cohort is included, so run these commands from the repository
root after installation:

```bash
python src/03_missing_data.py
python src/04_eda.py
python src/05_kaplan_meier.py
python src/06_km_by_grade.py
python src/07_cox_model.py
python src/08_preprocess_clinical.py
python src/09_naive_bayes_threshold.py
python src/10_smote_classification.py
python src/11_cox_full_analysis.py
python src/12_logrank_analysis.py
python src/13_cox_risk_km.py
python src/14_final_results_table.py
```

Scripts 01--02 require the excluded raw PDC manifest. On a headless machine,
set `MPLBACKEND=Agg` before running plot-producing scripts.

## Run the radiomics and combined-model analysis

1. Download CPTAC-PDA images and the tumour annotations from the linked TCIA
   resources, then convert a matched image/mask pair for each patient into the
   same physical space.
2. Create the manifest described in `data/raw/README.md`.
3. Extract features and compare models with out-of-fold C-indices:

```bash
python src/radiomics/01_extract_features.py --manifest data/raw/radiomics_manifest.csv
python src/radiomics/02_compare_survival_models.py
```

Install the optional image-processing dependencies first when running feature
extraction: `pip install -r requirements-radiomics.txt`.

The comparison only includes patients whose clinical identifier matches a
radiomics row. It writes `results/radiomics_model_comparison.csv`; report the
mean and standard deviation across folds, rather than training-set performance.

## Analysis Pipeline

Run the scripts in the following order:

### 1. Inspect clinical data

```bash
python src/01_inspect_data.py
```

This step is used to inspect the downloaded clinical manifests, understand their columns and identify the variables required for subsequent analysis.

### 2. Clean clinical data

```bash
python src/02_clean_clinical_data.py
```

This step cleans the relevant clinical variables and creates:

```text
data/processed/clinical_survival_clean.csv
```

### 3. Analyse missing data

```bash
python src/03_missing_data.py
```

Output:

```text
results/missing_data_report.csv
```

### 4. Exploratory data analysis

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

### 5. Overall Kaplan-Meier analysis

```bash
python src/05_kaplan_meier.py
```

Output:

```text
results/kaplan_meier_overall_survival.png
```

### 6. Kaplan-Meier analysis by tumor grade

```bash
python src/06_km_by_grade.py
```

Output:

```text
results/kaplan_meier_by_tumor_grade.png
```

### 7. Cox proportional hazards model

```bash
python src/07_cox_model.py
```

Output:

```text
results/cox_model_results.csv
```

## 8. Clinical Feature Preprocessing

```bash
python src/08_preprocess_clinical.py
```

Prepares clinical features using missing-value handling, categorical encoding and numerical standardization. Completely missing variables are removed.

Output:

```text
results/removed_clinical_features.csv
```

## 9. Naive Bayes Survival-Threshold Analysis

```bash
python src/09_naive_bayes_threshold.py
```

Tests the candidate survival thresholds:

- 240 days
- 270 days
- 300 days
- 330 days
- 360 days

Only patients with observed death times are used for this binary threshold-classification stage because censored observations do not provide a confirmed death time.

The current analysis selected **240 days** for the CPTAC-PDA cohort.

Output:

```text
results/naive_bayes_threshold_results.csv
```

## 10. SMOTE/SMOTENC Classification

```bash
python src/10_smote_classification.py
```

The selected threshold is used for binary classification. SMOTENC is applied only to the training data, and the untouched test set is used for evaluation.

Reported metrics include:

- Accuracy
- Balanced accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Confusion matrix

Outputs:

```text
results/smote_classification_results.csv
results/smote_class_distribution.csv
```

## 11. Clinical Cox Proportional Hazards Model

```bash
python src/11_cox_full_analysis.py
```

The clinical-only Cox model produces:

- Regression coefficients
- Hazard ratios
- 95% confidence intervals
- p-values
- Concordance index

Outputs:

```text
results/cox_full_results.csv
results/clinical_model_summary.csv
results/cox_proportional_hazards_test.csv
results/cox_removed_features.csv
```

## 12. Log-Rank Analysis Using Survival Threshold

```bash
python src/12_logrank_analysis.py
```

Patients are divided using the selected survival threshold and their Kaplan–Meier curves are compared using the log-rank test.

Outputs:

```text
results/logrank_threshold_results.csv
results/kaplan_meier_by_survival_threshold.png
```

Censored observations are retained for this survival analysis.

## 13. Cox-Based Risk Groups

```bash
python src/13_cox_risk_km.py
```

A partial-hazard risk score is obtained from the clinical Cox model. Patients are divided into Low Risk and High Risk groups using the median risk score.

Outputs:

```text
results/cox_risk_groups.csv
results/cox_risk_logrank_results.csv
results/kaplan_meier_cox_risk_groups.png
```

This risk-group analysis is descriptive and is not independent external validation because the risk scores are generated from the same cohort used to fit the model.

## 14. Final Clinical Results Table

```bash
python src/14_final_results_table.py
```

Collects the results from the preceding clinical-analysis stages without training another model.

Outputs:

```text
results/final_clinical_results.csv
results/final_clinical_model_summary.csv
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
