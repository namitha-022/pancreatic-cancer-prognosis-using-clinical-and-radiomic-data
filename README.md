# Pancreatic Cancer Prognosis Using Clinical and Radiomic Data

UE24CS352A machine-learning mini-project on prognosis prediction for pancreatic ductal adenocarcinoma (PDAC). It uses the public CPTAC-PDA cohort from The Cancer Imaging Archive (TCIA) to evaluate clinical, radiomics, and combined survival models.

**Team:** PES2UG24CS288 Muralikrishnan Menon and PES2UG24CS300 Namitha Ravikumar

## Project status

The clinical analysis is complete and reproducible. The committed processed cohort has 144 patients with usable survival data (115 deaths and 29 censored observations).

A radiomics pipeline (CT/RTSTRUCT conversion, feature extraction, cross-validated model comparison) is also included, and its output is committed in `results/radiomics_model_comparison.csv`. Raw clinical manifests, CT/MR images, tumour masks, and the extracted radiomics feature table are **not** committed because they are patient-level or large external data, so the radiomics comparison can only be re-run after you download the images (see [Run the radiomics pipeline](#run-the-radiomics-pipeline)).

### Results

| Analysis | Result | Interpretation |
| --- | --- | --- |
| Overall Kaplan-Meier median survival | 610 days (20.0 months) | Cohort-level estimate |
| Clinical Cox model (all 144 patients) | apparent C-index 0.680 | Exploratory, in-sample; not external validation |
| Threshold classifier | test balanced accuracy 0.417 | Poor predictive performance; not for clinical use |
| Cox risk groups | log-rank p = 1.82e-06 | Descriptive in-sample separation only |
| Clinical-only Cox (imaging subset, 5-fold CV) | mean C-index 0.616 (SD 0.210) | Out-of-fold |
| Radiomics-only Cox (imaging subset, 5-fold CV) | mean C-index 0.504 (SD 0.147) | No better than chance |
| Clinical + radiomics Cox (imaging subset, 5-fold CV) | mean C-index 0.649 (SD 0.209) | Small gain over clinical-only, well within fold-to-fold variation |

**Reading the radiomics results.** The imaging subset is small (only patients with a pre-treatment pancreas contour, a CT series, and clinical survival data; **N = <fill in from the output of `02_compare_survival_models.py`>**), so each CV fold holds roughly 9-10 patients and the fold-level C-indices range from 0.28 to 0.92. Radiomics alone carries no usable prognostic signal here, and the combined model's mean (0.649) is not distinguishable from clinical-only (0.616) given a standard deviation of about 0.21. These numbers should not be read as evidence that radiomics improves prognosis. Note also that the clinical-only CV score (0.616) is lower than the in-sample clinical C-index (0.680), as expected when moving from apparent to out-of-fold performance on a smaller cohort.

## Data

| Block | Source | Purpose |
| --- | --- | --- |
| Clinical and survival data | CPTAC clinical resources (PDC manifest) | Covariates, time, and event indicator |
| CT/MR imaging | [TCIA CPTAC-PDA](https://www.cancerimagingarchive.net/collection/cptac-pda/) | Image source for feature extraction |
| Tumour annotations | [TCIA CPTAC-PDA Tumor Annotations](https://www.cancerimagingarchive.net/analysis-result/cptac-pda-tumor-annotations/) | Pancreas contours (DICOM RTSTRUCT) |
| Radiomics | PyRadiomics, or the built-in lightweight extractor | Shape, first-order, and texture features |

**Imaging metadata included in the repo.** `data/raw/imaging/` contains two TCIA series-level metadata exports (series, study, and subject IDs and file locations; no image data):

- `annotation_metadata.csv`: 536 RTSTRUCT annotation series.
- `imaging_metadata.csv`: 168 image series (139 CT, 28 MR, 1 PT).

These are used by `src/radiomics/00_prepare_radiomics_data.py` and `15_match_patient.py` to link patients to their images and contours. Everything else under `data/raw/` is git-ignored. The expected local layout and manifest format are documented in [data/raw/README.md](data/raw/README.md). Do not commit downloaded images, masks, manifests, or patient-level raw data.

## Repository layout

```
data/
  processed/                    # Included cleaned clinical cohort
    clinical_survival_clean.csv     # 144 patients, survival time + event
    clinical_preprocessed.csv       # Encoded features for modelling
  raw/
    README.md                   # Instructions for excluded source data
    imaging/                    # TCIA series metadata (annotation + imaging CSVs)
results/                        # Clinical and radiomics tables and figures
src/
  01_inspect_data.py            # Inspect raw manifest (requires raw data)
  02_clean_clinical_data.py     # Build cleaned survival cohort (requires raw data)
  03_missing_data.py            # Missing-data report
  04_eda.py                     # Exploratory plots
  05_kaplan_meier.py            # Overall KM curve
  06_km_by_grade.py             # KM by tumour grade
  07_cox_model.py               # Initial Cox model
  08_preprocess_clinical.py     # Encoding / feature preparation
  09_naive_bayes_threshold.py   # Threshold classifier
  10_smote_classification.py    # SMOTE + Naive Bayes classification
  11_cox_full_analysis.py       # Full clinical Cox model
  12_logrank_analysis.py        # Log-rank tests
  13_cox_risk_km.py             # KM by Cox risk group
  14_final_results_table.py     # Final clinical summary tables
  radiomics/
    README.md                   # Radiomics pipeline details
    15_match_patient.py         # Patient overlap: clinical vs. annotations vs. imaging (see radiomics README)
    00_prepare_radiomics_data.py   # DICOM CT + RTSTRUCT -> NIfTI image/mask + manifest
    01_extract_features.py      # PyRadiomics feature extraction
    01b_extract_features_lite.py   # Lightweight extractor (no PyRadiomics needed)
    02_compare_survival_models.py  # Out-of-fold clinical / radiomics / combined comparison
requirements.txt
requirements-radiomics.txt
```

## Installation

```
python -m venv .venv
```

Windows:

```
.venv\Scripts\activate
```

Linux/macOS:

```
source .venv/bin/activate
```

```
pip install -r requirements.txt
```

For the radiomics pipeline, also install:

```
pip install -r requirements-radiomics.txt
```

PyRadiomics needs a C++ compiler on some systems. If it will not install, use `01b_extract_features_lite.py` instead (see below), which needs only SimpleITK, SciPy, and pandas.

## Reproduce the included clinical analysis

Run from the repository root. Scripts 03-14 work with the committed processed cohort; scripts 01-02 additionally require the excluded PDC clinical manifest.

```
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

On a headless system, set `MPLBACKEND=Agg` before running scripts that produce plots.

Key outputs include:

- `results/final_clinical_model_summary.csv`
- `results/final_clinical_results.csv`
- `results/kaplan_meier_overall_survival.png`
- `results/kaplan_meier_cox_risk_groups.png`

## Run the radiomics pipeline

See [src/radiomics/README.md](src/radiomics/README.md) for details. In short:

1. Download CPTAC-PDA CT images and the tumour annotations (RTSTRUCT) from TCIA. Keep the two TCIA metadata CSVs in `data/raw/imaging/` as `annotation_metadata.csv` and `imaging_metadata.csv`.
2. Convert each CT series and its pancreas contour to NIfTI and write the manifest `data/raw/radiomics_manifest.csv`:
   ```
   python src/radiomics/00_prepare_radiomics_data.py --dicom-root "D:/TCIA"
   ```
3. Extract features, using either PyRadiomics or the lightweight extractor (both write `data/processed/radiomics_features.csv`):
   ```
   python src/radiomics/01_extract_features.py --manifest data/raw/radiomics_manifest.csv
   # or, without PyRadiomics:
   python src/radiomics/01b_extract_features_lite.py --manifest data/raw/radiomics_manifest.csv
   ```
4. Compare models:
   ```
   python src/radiomics/02_compare_survival_models.py
   ```

Step 4 matches patients by `Case Submitter ID`, prints the matched cohort size, and writes `results/radiomics_model_comparison.csv`. It reports 5-fold out-of-fold C-indices (penalised Cox, penalizer 0.2, L1 ratio 0.5) for clinical-only, radiomics-only, and combined models. Imputation, encoding, and constant-feature filtering are fitted on each training fold only. Report the mean and standard deviation, not a training-set C-index.

## Survival endpoint and limitations

- `survival_time_days` is time to death for deceased patients and time to last follow-up for censored patients.
- `survival_event = 1` denotes death; `0` denotes right censoring.
- The clinical Cox and risk-group results are in-sample exploratory analyses.
- The threshold classifier excludes censored observations because a confirmed time of death is unavailable.
- The radiomics comparison uses a small subset of the cohort, a single contour per patient (the first `Pre-Dose PANCREAS` ROI), and one 5-fold split (seed 42). With so few events per fold and many candidate features, the estimates are noisy and no conclusion about radiomics should be drawn from them.
- Image features are not harmonised across scanners or contrast phases, and the lite extractor does not resample images.
- This project is for academic research only.
