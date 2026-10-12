"""Sanity-check the image/mask pairs: overlay PNGs + volume summary.

Run from the repo root:   python src/radiomics/04_check_masks.py
Needs: pip install matplotlib   (SimpleITK, numpy, pandas already installed)

Output: results/mask_check/<patient>.png  (CT slice with mask outline, 3 views)
        and a printed table of mask volumes in mL.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import SimpleITK as sitk

ROOT = Path(__file__).resolve().parents[2]


def resolve(p: str) -> str:
    q = Path(p)
    return str(q if q.is_absolute() else ROOT / q)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=ROOT / "data/raw/radiomics_manifest.csv")
    ap.add_argument("--n", type=int, default=6, help="how many patients to draw")
    args = ap.parse_args()

    out = ROOT / "results" / "mask_check"
    out.mkdir(parents=True, exist_ok=True)
    man = pd.read_csv(args.manifest)
    rows = []
    for k, rec in enumerate(man.to_dict("records")):
        img = sitk.ReadImage(resolve(rec["image_path"]))
        msk = sitk.ReadImage(resolve(rec["mask_path"]))
        a = sitk.GetArrayFromImage(img).astype(float)
        m = sitk.GetArrayFromImage(msk) > 0
        sp = img.GetSpacing()
        vol_ml = m.sum() * sp[0] * sp[1] * sp[2] / 1000
        zs, ys, xs = np.where(m)
        rows.append({"patient": rec["Case Submitter ID"], "mask_volume_ml": round(vol_ml, 1),
                     "mask_slices": len(set(zs)), "mean_HU_in_mask": round(a[m].mean(), 1),
                     "mean_HU_whole_scan": round(a.mean(), 1)})
        if k < args.n:
            z, y, x = int(np.median(zs)), int(np.median(ys)), int(np.median(xs))
            fig, ax = plt.subplots(1, 3, figsize=(13, 4.5))
            # Flip coronal/sagittal so head is up; overlay the mask with imshow (same origin as CT),
            # which avoids matplotlib's contour(origin=...) vertical-flip pitfall.
            views = [(a[z], m[z], "axial"),
                     (a[:, y, :][::-1], m[:, y, :][::-1], "coronal"),
                     (a[:, :, x][::-1], m[:, :, x][::-1], "sagittal")]
            for axis, (im, mk, name) in zip(ax, views):
                axis.imshow(np.clip(im, -150, 250), cmap="gray", origin="upper")
                axis.imshow(np.ma.masked_where(~mk, mk), cmap="autumn", alpha=0.55, origin="upper")
                axis.set_title(f"{rec['Case Submitter ID']} {name}")
                axis.axis("off")
            fig.tight_layout()
            fig.savefig(out / f"{rec['Case Submitter ID']}.png", dpi=90)
            plt.close(fig)
    df = pd.DataFrame(rows)
    df.to_csv(out / "mask_summary.csv", index=False)
    print(df.to_string(index=False))
    print("\nVolume summary (mL):", df.mask_volume_ml.describe().round(1).to_dict())
    print(f"\nOverlays saved in {out}. Open 2-3 PNGs: the red outline should sit on the pancreas")
    print("(a soft-tissue organ behind the stomach, near the spine/aorta), not on air, bone or the wrong side.")


if __name__ == "__main__":
    main()
