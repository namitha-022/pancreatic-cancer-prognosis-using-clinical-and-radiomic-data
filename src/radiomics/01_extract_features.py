"""Extract one PyRadiomics feature row per tumour ROI.

Input is a CSV manifest with Case Submitter ID, image_path and mask_path.
Images and masks must already be co-registered. This deliberately does not
try to guess DICOM-SEG references: validate the conversion before extraction.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from radiomics import featureextractor


ROOT = Path(__file__).resolve().parents[2]


def resolve_path(value: str) -> str:
    path = Path(value)
    return str(path if path.is_absolute() else ROOT / path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "data" / "processed" / "radiomics_features.csv",
    )
    parser.add_argument("--params", type=Path, help="Optional PyRadiomics YAML settings")
    args = parser.parse_args()

    manifest = pd.read_csv(args.manifest)
    required = {"Case Submitter ID", "image_path", "mask_path"}
    missing = required.difference(manifest.columns)
    if missing:
        raise ValueError(f"Manifest is missing columns: {sorted(missing)}")
    if manifest["Case Submitter ID"].duplicated().any():
        raise ValueError("Manifest must contain exactly one image/mask pair per patient.")

    extractor = featureextractor.RadiomicsFeatureExtractor(str(args.params)) if args.params else featureextractor.RadiomicsFeatureExtractor()
    rows = []
    for record in manifest.to_dict("records"):
        image, mask = resolve_path(record["image_path"]), resolve_path(record["mask_path"])
        if not Path(image).exists() or not Path(mask).exists():
            raise FileNotFoundError(f"Missing image or mask for {record['Case Submitter ID']}")
        features = extractor.execute(image, mask)
        # Diagnostics describe processing, not quantitative radiomic features.
        features = {key: value for key, value in features.items() if not key.startswith("diagnostics_")}
        rows.append({"Case Submitter ID": record["Case Submitter ID"], **features})

    output = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)
    print(f"Wrote {len(output)} patients and {len(output.columns) - 1} features to {args.output}")


if __name__ == "__main__":
    main()
