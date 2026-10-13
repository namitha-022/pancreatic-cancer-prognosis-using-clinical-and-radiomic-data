# Pancreatic Cancer Prognosis Using Clinical and Radiomic Data

UE24CS352A machine-learning mini-project on prognosis prediction for pancreatic ductal adenocarcinoma (PDAC). It uses the public CPTAC-PDA cohort from The Cancer Imaging Archive (TCIA) to evaluate clinical, radiomics, and combined survival models.

**Team:** PES2UG24CS288 Muralikrishnan Menon and PES2UG24CS300 Namitha Ravikumar

## Project status

The clinical analysis is complete and reproducible. The committed processed cohort has 144 patients with usable survival data (115 deaths and 29 censored observations).

A radiomics pipeline (CT/RTSTRUCT conversion, feature extraction, cross-validated model comparison) is also included. Its outputs are committed in `results/radiomics_model_comparison.csv` (a single 5-fold run) and `results/radiomics_improved_comparison.csv` (5-fold cross-validation repeated 20 times, the main radiomics result). Raw clinical manifests, CT/MR images, tumour masks, and the extracted radiomics feature table are **not** committed because they are patient-level or large external data, so the radiomics comparison can only be re-run after you download the images (see [Run the radiomics pipeline](#run-the-radiomics-pipeline)).

### Results

| Analysis | Result | Interpretation |
| --- | --- | --- |
| Overall Kaplan-Meier median survival | 610 days (20.0 months) | Cohort-level estimate |
| Clinical Cox model (all 144 patients) | apparent C-index 0.680 | Exploratory, in-sample; not external validation |
| Threshold classifier | test balanced accuracy 0.417 | Poor predictive performance; not for clinical use |
| Cox risk groups | log-rank p = 1.82e-06 | Descriptive in-sample separation only |
| Clinical-only Cox (46-patient imaging subset, 5-fold CV x 20) | mean C-index 0.648 (SD 0.054) | Out-of-fold |
| Radiomics-only Cox, all 25 features | mean C-index 0.522 (SD 0.040) | No better than chance |
| Radiomics-only Cox, 3 best features (chosen inside each training fold) | mean C-index 0.559 (SD 0.065) | Close to chance |
| Clinical + radiomics Cox, all 25 features | mean C-index 0.600 (SD 0.042) | Below clinical-only |
| Clinical + radiomics Cox, 3 best features | mean C-index 0.620 (SD 0.041) | Below clinical-only; radiomics adds no gain |

SD is the standard deviation of the mean C-index across the 20 repeats. C-index 0.5 means a random ranking and 1.0 a perfect one.

**Reading the radiomics results.** The imaging subset is small: **N = 46** patients who have a clinical survival record, a pre-treatment CT series and a pre-treatment pancreas contour, so each CV fold holds about nine patients. A single 5-fold run (`02_compare_survival_models.py`, seed 42; clinical 0.616, radiomics 0.504, combined 0.649) suggested a small gain from radiomics, but its fold scores ranged from 0.28 to 0.92 and the gain disappeared once the cross-validation was repeated 20 times (`03_radiomics_improved.py`). The repeated run is therefore the main result: radiomics alone is close to chance, and adding it to the clinical model does not beat the clinical model alone. These numbers should not be read as evidence that radiomics improves prognosis. The clinical-only CV score (0.648) is lower than the in-sample C-index on all patients (0.680), as expected when moving from apparent to out-of-fold performance on a smaller cohort.

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
    04_check_masks.py              # Overlay PNGs and mask volumes to check the masks
    01_extract_features.py      # PyRadiomics feature extraction
    01b_extract_features_lite.py   # Lightweight extractor (no PyRadiomics needed)
    02_compare_survival_models.py  # Single 5-fold clinical / radiomics / combined comparison
    03_radiomics_improved.py       # Repeated CV with in-fold feature selection (main result)
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
2. Convert each CT series and its pancreas contour to NIfTI and write the manifest `data/raw/radiomics_manifest.csv`. If the images and annotations are in separate download folders, pass both:
   ```
   python src/radiomics/00_prepare_radiomics_data.py --dicom-root "D:/images" "D:/annotations"
   ```
3. (Optional check) Draw the masks over the CT and print their volumes in `results/mask_check/`:
   ```
   python src/radiomics/04_check_masks.py
   ```
4. Extract features, using either PyRadiomics or the lightweight extractor (both write `data/processed/radiomics_features.csv`):
   ```
   python src/radiomics/01_extract_features.py --manifest data/raw/radiomics_manifest.csv
   # or, without PyRadiomics:
   python src/radiomics/01b_extract_features_lite.py --manifest data/raw/radiomics_manifest.csv
   ```
5. Compare models with a single 5-fold split:
   ```
   python src/radiomics/02_compare_survival_models.py
   ```
6. Repeat the comparison 20 times with in-fold feature selection (main result):
   ```
   python src/radiomics/03_radiomics_improved.py
   ```

Step 5 matches patients by `Case Submitter ID`, prints the matched cohort size, and writes `results/radiomics_model_comparison.csv`. It reports 5-fold out-of-fold C-indices (penalised Cox, penalizer 0.2, L1 ratio 0.5) for clinical-only, radiomics-only, and combined models. Step 6 repeats 5-fold CV 20 times; in each training fold it standardises the features, keeps the 3 radiomic features most associated with survival (ranked by univariate C-index on the training patients only), and fits a ridge-penalised Cox model (penalizer 0.5). It also reports the all-25-feature models as a baseline and writes `results/radiomics_improved_comparison.csv`. In both steps imputation, encoding, and feature selection use training folds only. Report the mean and standard deviation, not a training-set C-index.

## Survival endpoint and limitations

- `survival_time_days` is time to death for deceased patients and time to last follow-up for censored patients.
- `survival_event = 1` denotes death; `0` denotes right censoring.
- The clinical Cox and risk-group results are in-sample exploratory analyses.
- The threshold classifier excludes censored observations because a confirmed time of death is unavailable.
- The radiomics comparison uses a small subset of the cohort (N = 46), one CT series and the first `Pre-Dose PANCREAS` contour per patient, and a custom 25-feature extractor. Even with repeated cross-validation, the estimates are noisy, and no firm conclusion about radiomics should be drawn from them.
- Five patients with a contour on MR rather than CT were left out, because CT and MR intensities are not comparable. Some CT scans have uneven slice spacing.
- `04_check_masks.py` flagged six patients whose mean intensity inside the mask is below 0 HU (possibly a mask on fat or air). They were kept in the analysis.
- Image features are not harmonised across scanners or contrast phases, and the lite extractor does not resample images.
- This project is for academic research only.
