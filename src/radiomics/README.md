# Radiomics Pipeline

This folder holds the CPTAC-PDA imaging and radiomics pipeline. It turns CT scans and tumour contours into image features, then checks whether those features help predict survival beyond clinical data.

Run the scripts from the repository root, in this order. Install `requirements.txt` and `requirements-radiomics.txt` first.

| Order | Script | What it does | Output |
| --- | --- | --- | --- |
| 1 | `00_prepare_radiomics_data.py` | Picks one pre-treatment CT series and the `Pre-Dose PANCREAS` contour per patient, converts the CT to NIfTI and the contour to a binary mask | `data/raw/radiomics_nifti/` and `data/raw/radiomics_manifest.csv` |
| 2 | `04_check_masks.py` | Draws each mask over its CT and prints the mask volume and mean intensity (sanity check) | `results/mask_check/` |
| 3a | `01_extract_features.py` | Extracts PyRadiomics features (needs a C++ compiler on some systems) | `data/processed/radiomics_features.csv` |
| 3b | `01b_extract_features_lite.py` | Same job without PyRadiomics: 25 shape, intensity and texture features | `data/processed/radiomics_features.csv` |
| 4 | `02_compare_survival_models.py` | Single 5-fold comparison of clinical, radiomics and combined Cox models | `results/radiomics_model_comparison.csv` |
| 5 | `03_radiomics_improved.py` | 5-fold CV repeated 20 times; keeps the 3 best radiomic features inside each training fold (main result) | `results/radiomics_improved_comparison.csv` |
| - | `15_match_patient.py` | Counts how many patients appear in the clinical data, the annotations and the imaging | printed table |

Use either 3a or 3b, not both.

## Data needed

- The two TCIA metadata CSVs in `data/raw/imaging/`: `annotation_metadata.csv` (contours) and `imaging_metadata.csv` (scans).
- The downloaded DICOM folders. If the images and annotations are in separate download folders, give both: `--dicom-root "D:/images" "D:/annotations"`.
- `data/processed/clinical_survival_clean.csv` (already in the repository).

## Notes

- `00` reads which CT series each contour was drawn on from the contour file and falls back to the largest CT series in the same study. It skips patients without a usable CT and prints why.
- Only CT is used. Five patients have their contour on MR scans and are left out, because CT and MR intensities cannot be compared.
- The final cohort is 46 patients with clinical survival data, a CT and a pancreas contour. Intensities are clipped to -150..250 HU and texture uses 25 HU bins. Images are not resampled.
- `15_match_patient.py` expects the annotation file name set at the top of the script. Change `ANNOTATION_FILE` to `annotation_metadata.csv` if you use the file names above.
- Raw images, masks, the manifest and the feature table are not committed (patient-level or large data).
