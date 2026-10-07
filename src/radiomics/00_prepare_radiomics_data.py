"""Prepare image/mask pairs for PyRadiomics from TCIA CPTAC-PDA downloads.

For each patient that has (a) a pre-treatment PANCREAS RTSTRUCT contour,
(b) a downloaded CT series, and (c) a row in the clinical survival table, this
script:
  1. picks the CT series the contour was drawn on (ReferencedSeriesInstanceUID),
  2. converts that CT series to NIfTI,
  3. rasterises the contour into a binary mask on the same grid,
  4. writes data/raw/radiomics_manifest.csv with the columns
     Case Submitter ID,image_path,mask_path

Setup (run from the repository root):
    pip install pydicom rt-utils SimpleITK pandas
    Put the two TCIA metadata CSVs in data/raw/imaging/ as
        annotation_metadata.csv   (the RTSTRUCT / tumour-annotation CSV)
        imaging_metadata.csv      (the CT/MR CSV)
    Set --dicom-root to the folder that contains the "CPTAC-PDA" download
    (the folder the "File Location" column paths start from).

Usage:
    python src/radiomics/00_prepare_radiomics_data.py --dicom-root "D:/TCIA"
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import pydicom
import SimpleITK as sitk
from rt_utils import RTStructBuilder

ROOT = Path(__file__).resolve().parents[2]
ID = "Case Submitter ID"
ROI_REGEX = r"^Pre-Dose PANCREAS - \d+$"  # excludes "SEED POINT", liver, nodes, post-chemo


def to_path(dicom_root: Path, file_location: str) -> Path:
    """TCIA 'File Location' uses Windows separators and a leading '.\\'."""
    parts = [p for p in file_location.replace("\\", "/").split("/") if p not in ("", ".")]
    return dicom_root.joinpath(*parts)


def find_rtstruct_file(folder: Path) -> Path:
    files = sorted(folder.glob("*.dcm"))
    if not files:
        raise FileNotFoundError(f"No .dcm file in {folder}")
    return files[0]


def referenced_series_uid(rt_file: Path) -> str | None:
    """CT series UID that the contour was drawn on (read from the RTSTRUCT header)."""
    ds = pydicom.dcmread(rt_file, stop_before_pixels=True)
    try:
        frame = ds.ReferencedFrameOfReferenceSequence[0]
        study = frame.RTReferencedStudySequence[0]
        return str(study.RTReferencedSeriesSequence[0].SeriesInstanceUID)
    except (AttributeError, IndexError):
        return None


def convert_one(patient: str, ct_dir: Path, rt_file: Path, out_dir: Path) -> tuple[Path, Path]:
    image_out = out_dir / "images" / f"{patient}.nii.gz"
    mask_out = out_dir / "masks" / f"{patient}.nii.gz"
    image_out.parent.mkdir(parents=True, exist_ok=True)
    mask_out.parent.mkdir(parents=True, exist_ok=True)

    # CT series -> NIfTI (SimpleITK sorts slices by position).
    reader = sitk.ImageSeriesReader()
    names = reader.GetGDCMSeriesFileNames(str(ct_dir))
    reader.SetFileNames(names)
    image = reader.Execute()
    sitk.WriteImage(image, str(image_out))

    # Contour -> boolean mask (rt_utils returns [rows, cols, slices]).
    rtstruct = RTStructBuilder.create_from(dicom_series_path=str(ct_dir), rt_struct_path=str(rt_file))
    names_in_file = rtstruct.get_roi_names()
    wanted = [n for n in names_in_file if "PANCREAS" in n.upper() and "DUCT" not in n.upper()]
    if not wanted:
        raise ValueError(f"No PANCREAS ROI in {rt_file.name}; ROIs: {names_in_file}")
    mask_arr = rtstruct.get_roi_mask_by_name(wanted[0])  # bool, (rows, cols, slices)
    mask_arr = np.transpose(mask_arr, (2, 0, 1)).astype(np.uint8)  # -> (slices, rows, cols)
    mask = sitk.GetImageFromArray(mask_arr)
    mask.CopyInformation(image)
    if mask_arr.sum() == 0:
        raise ValueError("Empty mask after rasterisation")
    sitk.WriteImage(mask, str(mask_out))
    return image_out, mask_out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dicom-root", required=True, type=Path)
    ap.add_argument("--annotations", type=Path, default=ROOT / "data/raw/imaging/annotation_metadata.csv")
    ap.add_argument("--imaging", type=Path, default=ROOT / "data/raw/imaging/imaging_metadata.csv")
    ap.add_argument("--out", type=Path, default=ROOT / "data/raw/radiomics_nifti")
    ap.add_argument("--manifest", type=Path, default=ROOT / "data/raw/radiomics_manifest.csv")
    args = ap.parse_args()

    clinical = pd.read_csv(ROOT / "data/processed/clinical_survival_clean.csv")
    clinical_ids = set(clinical[ID].astype(str).str.strip())

    ann = pd.read_csv(args.annotations)
    img = pd.read_csv(args.imaging)
    ann = ann[ann["Series Description"].str.match(ROI_REGEX)]
    ann = ann[ann["Subject ID"].isin(clinical_ids)]
    img = img[img["Modality"] == "CT"]

    manifest_rows, skipped = [], []
    for patient, group in ann.groupby("Subject ID"):
        try:
            # Several contours can exist; try each until one converts cleanly.
            done = False
            for _, rt in group.iterrows():
                rt_file = find_rtstruct_file(to_path(args.dicom_root, rt["File Location"]))
                ref_uid = referenced_series_uid(rt_file)
                candidates = img[img["Study UID"] == rt["Study UID"]]
                if ref_uid is not None:
                    exact = candidates[candidates["Series UID"] == ref_uid]
                    candidates = exact if len(exact) else candidates
                if candidates.empty:
                    continue
                ct_row = candidates.sort_values("Number of Images", ascending=False).iloc[0]
                ct_dir = to_path(args.dicom_root, ct_row["File Location"])
                image_path, mask_path = convert_one(patient, ct_dir, rt_file, args.out)
                manifest_rows.append({ID: patient, "image_path": str(image_path), "mask_path": str(mask_path)})
                print(f"OK    {patient}")
                done = True
                break
            if not done:
                skipped.append((patient, "no matching CT series downloaded"))
        except Exception as exc:  # keep going; report at the end
            skipped.append((patient, f"{type(exc).__name__}: {exc}"))
            print(f"SKIP  {patient}: {exc}")

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(manifest_rows).to_csv(args.manifest, index=False)
    print(f"\nWrote {len(manifest_rows)} pairs to {args.manifest}")
    if skipped:
        print(f"Skipped {len(skipped)} patients:")
        for patient, why in skipped:
            print(f"  {patient}: {why}")


if __name__ == "__main__":
    main()
