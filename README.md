# Pancreatic Cancer Prognosis Using Clinical and Radiomic Data

UE24CS352A machine-learning mini-project on prognosis prediction for pancreatic ductal adenocarcinoma (PDAC). It uses the public CPTAC-PDA cohort from The Cancer Imaging Archive (TCIA) to evaluate clinical, radiomics, and combined survival models.

**Team:** PES2UG24CS288 Muralikrishnan Menon and PES2UG24CS300 Namitha Ravikumar

## Project status

The included clinical analysis is complete and reproducible. The committed processed cohort has 144 patients with usable survival data (115 deaths and 29 censored observations). Raw clinical manifests, CT/MR images, tumour masks, and radiomics features are not committed because they are patient-level or large external data. Therefore, this repository makes **no claim** about radiomics or combined-model performance until those data are supplied.

| Analysis | Result | Interpretation |
| --- | ---: | --- |
| Overall Kaplan-Meier median survival | 610 days (20.0 months) | Cohort-level estimate |
| Clinical Cox model | apparent C-index 0.680 | Exploratory; not external validation |
| Threshold classifier | test balanced accuracy 0.417 | Poor predictive performance; not for clinical use |
| Cox risk groups | log-rank p = 1.82e-06 | Descriptive in-sample separation only |

## Data

| Block | Source | Purpose |
| --- | --- | --- |
| Clinical and survival data | CPTAC clinical resources | Covariates, time, and event indicator |
| CT/MR imaging | [TCIA CPTAC-PDA](https://www.cancerimagingarchive.net/collection/cptac-pda/) | Image source for feature extraction |
| Tumour annotations | [TCIA CPTAC-PDA Tumor Annotations](https://www.cancerimagingarchive.net/analysis-result/cptac-pda-tumor-annotations/) | Tumour regions of interest |
| Radiomics | PyRadiomics | First-order, shape, and texture features |

The expected local raw-data layout and radiomics manifest are documented in [data/raw/README.md](data/raw/README.md). Do not commit downloaded images, masks, manifests, or patient-level raw data.

## Repository layout

```text
data/
  processed/                  # Included cleaned clinical cohort
  raw/README.md               # Instructions for excluded source data
results/                      # Reproduced clinical tables and figures
src/
  01_inspect_data.py          # Inspect raw manifest (requires raw data)
  02_clean_clinical_data.py   # Build cleaned survival cohort (requires raw data)
  03_...14_*.py               # Clinical analysis pipeline
  radiomics/
    01_extract_features.py    # PyRadiomics extraction from image/mask manifest
    02_compare_survival_models.py # Out-of-fold model comparison
requirements.txt
requirements-radiomics.txt
```

## Installation

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

For image feature extraction, also install:

```bash
pip install -r requirements-radiomics.txt
```

## Reproduce the included clinical analysis

Run from the repository root. Scripts 03--14 work with the committed processed cohort; scripts 01--02 additionally require the excluded PDC clinical manifest.

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

On a headless system, set `MPLBACKEND=Agg` before running scripts that produce plots.

Key outputs include:

- `results/final_clinical_model_summary.csv`
- `results/final_clinical_results.csv`
- `results/kaplan_meier_overall_survival.png`
- `results/kaplan_meier_cox_risk_groups.png`

## Run radiomics and combined survival models

1. Download CPTAC-PDA images and tumour annotations from TCIA.
2. Convert each image and matching tumour mask into the same physical space (for example NIfTI or NRRD).
3. Create `data/raw/radiomics_manifest.csv` as specified in [data/raw/README.md](data/raw/README.md).
4. Run:

```bash
python src/radiomics/01_extract_features.py --manifest data/raw/radiomics_manifest.csv
python src/radiomics/02_compare_survival_models.py
```

The second command matches patients by `Case Submitter ID` and writes `results/radiomics_model_comparison.csv`. It reports 5-fold out-of-fold C-indices for clinical-only, radiomics-only, and combined penalised Cox models. Report the mean and standard deviation, rather than a training-set C-index.

## Survival endpoint and limitations

- `survival_time_days` is time to death for deceased patients and time to last follow-up for censored patients.
- `survival_event = 1` denotes death; `0` denotes right censoring.
- The clinical Cox and risk-group results are in-sample exploratory analyses.
- The threshold classifier excludes censored observations because a confirmed time of death is unavailable.
- This project is for academic research only and is not a clinical decision support tool.
