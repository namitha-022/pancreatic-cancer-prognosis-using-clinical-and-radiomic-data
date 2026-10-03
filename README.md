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
