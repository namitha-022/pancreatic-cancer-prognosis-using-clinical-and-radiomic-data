"""Lightweight radiomics extractor (no PyRadiomics / no C++ compiler needed).

Drop-in replacement for 01_extract_features.py. Same input manifest
(Case Submitter ID, image_path, mask_path) and same output file
(data/processed/radiomics_features.csv), so 02_compare_survival_models.py
runs unchanged.

Features (25 per patient, deliberately few for a ~45-patient cohort):
  * shape       : volume, surface area, max 3D diameter, sphericity, elongation
  * first-order : mean, std, min, max, range, median, skewness, kurtosis,
                  entropy, energy, 10th/90th percentile, interquartile range
  * texture     : 3D grey-level co-occurrence matrix (GLCM, 13 directions
                  averaged) -> contrast, dissimilarity, homogeneity, ASM,
                  energy, entropy, correlation

Method notes (state these in the write-up):
  * intensities are Hounsfield units, clipped to [-150, 250] inside the mask to
    limit the effect of calcifications / air,
  * texture uses fixed-bin-width discretisation (bin width 25 HU),
  * the image is NOT resampled; voxel spacing is used for shape features only.
"""
from __future__ import annotations

import argparse
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
import SimpleITK as sitk
from scipy import ndimage, stats
from scipy.spatial.distance import pdist

ROOT = Path(__file__).resolve().parents[2]
ID = "Case Submitter ID"
HU_MIN, HU_MAX, BIN_WIDTH = -150.0, 250.0, 25.0

# 13 unique 3D directions (half of the 26 neighbours).
DIRECTIONS = [d for d in product((-1, 0, 1), repeat=3) if d > (0, 0, 0)]


def resolve_path(value: str) -> str:
    path = Path(value)
    return str(path if path.is_absolute() else ROOT / path)


def shape_features(mask: np.ndarray, spacing_zyx: tuple[float, float, float]) -> dict:
    voxel_vol = float(np.prod(spacing_zyx))
    volume = mask.sum() * voxel_vol
    eroded = ndimage.binary_erosion(mask)
    surface_voxels = mask & ~eroded
    # Surface area approximated from exposed voxel faces.
    area = 0.0
    sz, sy, sx = spacing_zyx
    face_area = {0: sy * sx, 1: sz * sx, 2: sz * sy}
    padded = np.pad(mask, 1)
    for axis in range(3):
        for shift in (-1, 1):
            neighbour = np.roll(padded, shift, axis=axis)[1:-1, 1:-1, 1:-1]
            area += (mask & ~neighbour).sum() * face_area[axis]
    sphericity = (np.pi ** (1 / 3)) * ((6 * volume) ** (2 / 3)) / area if area > 0 else np.nan

    coords = np.argwhere(surface_voxels) * np.array(spacing_zyx)
    if len(coords) > 2000:  # subsample for speed
        coords = coords[np.random.default_rng(0).choice(len(coords), 2000, replace=False)]
    max_diam = float(pdist(coords).max()) if len(coords) > 1 else np.nan

    all_coords = np.argwhere(mask) * np.array(spacing_zyx)
    eigvals = np.sort(np.linalg.eigvalsh(np.cov(all_coords.T)))[::-1] if len(all_coords) > 3 else [np.nan] * 3
    elongation = float(np.sqrt(eigvals[1] / eigvals[0])) if eigvals[0] > 0 else np.nan
    return {
        "shape_volume_mm3": volume,
        "shape_surface_area_mm2": area,
        "shape_max_diameter_mm": max_diam,
        "shape_sphericity": sphericity,
        "shape_elongation": elongation,
    }


def firstorder_features(values: np.ndarray) -> dict:
    hist, _ = np.histogram(values, bins=np.arange(HU_MIN, HU_MAX + BIN_WIDTH, BIN_WIDTH))
    p = hist / hist.sum()
    p = p[p > 0]
    q10, q25, q50, q75, q90 = np.percentile(values, [10, 25, 50, 75, 90])
    return {
        "firstorder_mean": values.mean(),
        "firstorder_std": values.std(),
        "firstorder_min": values.min(),
        "firstorder_max": values.max(),
        "firstorder_range": values.max() - values.min(),
        "firstorder_median": q50,
        "firstorder_skewness": stats.skew(values),
        "firstorder_kurtosis": stats.kurtosis(values),
        "firstorder_entropy": float(-(p * np.log2(p)).sum()),
        "firstorder_energy": float((values ** 2).sum()),
        "firstorder_p10": q10,
        "firstorder_p90": q90,
        "firstorder_iqr": q75 - q25,
    }


def glcm_features(image: np.ndarray, mask: np.ndarray) -> dict:
    levels = int(np.ceil((HU_MAX - HU_MIN) / BIN_WIDTH))
    binned = np.clip(((image - HU_MIN) // BIN_WIDTH).astype(int), 0, levels - 1)
    glcm = np.zeros((levels, levels), dtype=np.float64)
    shape = np.array(mask.shape)
    for d in DIRECTIONS:
        src = tuple(slice(max(0, -o), s - max(0, o)) for o, s in zip(d, shape))
        dst = tuple(slice(max(0, o), s - max(0, -o)) for o, s in zip(d, shape))
        valid = mask[src] & mask[dst]
        a, b = binned[src][valid], binned[dst][valid]
        np.add.at(glcm, (a, b), 1)
        np.add.at(glcm, (b, a), 1)  # symmetric
    total = glcm.sum()
    if total == 0:
        return {f"glcm_{n}": np.nan for n in ("contrast", "dissimilarity", "homogeneity", "asm", "energy", "entropy", "correlation")}
    p = glcm / total
    i, j = np.indices(p.shape)
    mu_i, mu_j = (i * p).sum(), (j * p).sum()
    sd_i = np.sqrt(((i - mu_i) ** 2 * p).sum())
    sd_j = np.sqrt(((j - mu_j) ** 2 * p).sum())
    nz = p[p > 0]
    asm = float((p ** 2).sum())
    return {
        "glcm_contrast": float(((i - j) ** 2 * p).sum()),
        "glcm_dissimilarity": float((np.abs(i - j) * p).sum()),
        "glcm_homogeneity": float((p / (1 + (i - j) ** 2)).sum()),
        "glcm_asm": asm,
        "glcm_energy": float(np.sqrt(asm)),
        "glcm_entropy": float(-(nz * np.log2(nz)).sum()),
        "glcm_correlation": float(((i - mu_i) * (j - mu_j) * p).sum() / (sd_i * sd_j)) if sd_i * sd_j > 0 else np.nan,
    }


def extract(image_path: str, mask_path: str) -> dict:
    image = sitk.ReadImage(image_path)
    mask = sitk.ReadImage(mask_path)
    spacing_zyx = tuple(reversed(image.GetSpacing()))
    img_arr = sitk.GetArrayFromImage(image).astype(np.float64)
    mask_arr = sitk.GetArrayFromImage(mask) > 0
    if img_arr.shape != mask_arr.shape:
        raise ValueError(f"image {img_arr.shape} and mask {mask_arr.shape} differ")
    if mask_arr.sum() < 50:
        raise ValueError("mask has fewer than 50 voxels")
    # Crop to the mask's bounding box (+1 voxel margin) so texture is fast.
    zz, yy, xx = np.where(mask_arr)
    box = tuple(slice(max(0, a.min() - 1), a.max() + 2) for a in (zz, yy, xx))
    img_arr, mask_arr = img_arr[box], mask_arr[box]
    clipped = np.clip(img_arr, HU_MIN, HU_MAX)
    values = clipped[mask_arr]
    features = {}
    features.update(shape_features(mask_arr, spacing_zyx))
    features.update(firstorder_features(values))
    features.update(glcm_features(clipped, mask_arr))
    return features


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "processed" / "radiomics_features.csv")
    args = parser.parse_args()

    manifest = pd.read_csv(args.manifest)
    required = {ID, "image_path", "mask_path"}
    if required - set(manifest.columns):
        raise ValueError(f"Manifest is missing columns: {sorted(required - set(manifest.columns))}")
    if manifest[ID].duplicated().any():
        raise ValueError("Manifest must contain exactly one image/mask pair per patient.")

    rows, failed = [], []
    for n, record in enumerate(manifest.to_dict("records"), start=1):
        try:
            feats = extract(resolve_path(record["image_path"]), resolve_path(record["mask_path"]))
            rows.append({ID: record[ID], **feats})
            print(f"[{n}/{len(manifest)}] OK   {record[ID]}")
        except Exception as exc:
            failed.append((record[ID], str(exc)))
            print(f"[{n}/{len(manifest)}] SKIP {record[ID]}: {exc}")

    output = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)
    print(f"\nWrote {len(output)} patients and {len(output.columns) - 1} features to {args.output}")
    for patient, why in failed:
        print(f"  skipped {patient}: {why}")


if __name__ == "__main__":
    main()
