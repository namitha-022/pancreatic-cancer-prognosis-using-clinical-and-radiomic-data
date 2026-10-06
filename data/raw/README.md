# Raw data (not version controlled)

This repository intentionally does **not** contain patient-level source data,
CT/MR images, or segmentation masks. Download them from the CPTAC-PDA TCIA
collection and its CPTAC-PDA Tumor Annotations analysis result, subject to
their terms of use.

Place the PDC clinical manifest at:

`data/raw/PDC_clinical_manifest_10032026_200348.csv`

The clinical cleaning scripts require the columns listed in
`src/02_clean_clinical_data.py`. The processed clinical cohort already
committed to this repository contains 144 usable survival records, so steps
03--14 can be reproduced without the raw manifest.

For radiomics, convert each selected image series and its matching tumour mask
to the same physical space (for example, NIfTI or NRRD). Make a CSV manifest
with these exact columns:

```text
Case Submitter ID,image_path,mask_path
C3L-01687,C:/data/images/C3L-01687.nii.gz,C:/data/masks/C3L-01687.nii.gz
```

Paths may be absolute or relative to the repository root. Do not commit this
manifest, the images, or masks.
