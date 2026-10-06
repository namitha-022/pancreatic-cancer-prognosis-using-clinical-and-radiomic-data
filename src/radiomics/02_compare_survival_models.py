"""Compare clinical, radiomics, and combined Cox models with held-out folds.

The feature table must contain ``Case Submitter ID`` plus numeric radiomics
columns. Results are out-of-fold C-indices, not apparent (training-set)
performance. Feature filtering is fitted independently within each training
fold to avoid test-set leakage.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index
from sklearn.model_selection import KFold


ROOT = Path(__file__).resolve().parents[2]
ID, TIME, EVENT = "Case Submitter ID", "survival_time_days", "survival_event"


def design_matrix(train: pd.DataFrame, test: pd.DataFrame, columns: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Impute/encode using training data only and align test columns."""
    train_x, test_x = train[columns].copy(), test[columns].copy()
    numeric = train_x.select_dtypes(include=np.number).columns.tolist()
    categorical = [name for name in columns if name not in numeric]
    for name in numeric:
        median = train_x[name].median()
        train_x[name] = train_x[name].fillna(median)
        test_x[name] = test_x[name].fillna(median)
    for name in categorical:
        train_x[name] = train_x[name].fillna("Unknown").astype(str)
        test_x[name] = test_x[name].fillna("Unknown").astype(str)
    train_x = pd.get_dummies(train_x, columns=categorical, drop_first=True, dtype=float)
    test_x = pd.get_dummies(test_x, columns=categorical, drop_first=True, dtype=float).reindex(columns=train_x.columns, fill_value=0)
    # Constant features make a Cox model singular.
    keep = train_x.columns[train_x.nunique() > 1]
    return train_x[keep], test_x[keep]


def fold_score(train: pd.DataFrame, test: pd.DataFrame, features: list[str]) -> float:
    train_x, test_x = design_matrix(train, test, features)
    model_train = pd.concat([train[[TIME, EVENT]].reset_index(drop=True), train_x.reset_index(drop=True)], axis=1)
    cph = CoxPHFitter(penalizer=0.2, l1_ratio=0.5)
    cph.fit(model_train, duration_col=TIME, event_col=EVENT)
    risk = cph.predict_partial_hazard(test_x).to_numpy().ravel()
    return concordance_index(test[TIME], -risk, test[EVENT])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radiomics", type=Path, default=ROOT / "data" / "processed" / "radiomics_features.csv")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    clinical = pd.read_csv(ROOT / "data" / "processed" / "clinical_survival_clean.csv")
    radiomics = pd.read_csv(args.radiomics)
    if ID not in radiomics:
        raise ValueError(f"{args.radiomics} must include '{ID}'.")
    if radiomics[ID].duplicated().any():
        raise ValueError("Radiomics table must have one row per patient.")
    radiomics_cols = [name for name in radiomics.columns if name != ID and pd.api.types.is_numeric_dtype(radiomics[name])]
    if not radiomics_cols:
        raise ValueError("No numeric radiomics features were found.")

    data = clinical.merge(radiomics[[ID] + radiomics_cols], on=ID, how="inner").dropna(subset=[TIME, EVENT])
    if len(data) < args.folds * 2:
        raise ValueError("Too few matched patients for the requested number of folds.")
    clinical_cols = [name for name in clinical.columns if name not in {ID, TIME, EVENT, "survival_time_months", "Days to Death", "Days to Last Follow Up", "Vital Status", "Age at Diagnosis"}]
    clinical_cols = [name for name in clinical_cols if data[name].notna().any()]

    models = {"clinical": clinical_cols, "radiomics": radiomics_cols, "combined": clinical_cols + radiomics_cols}
    rows = []
    splitter = KFold(n_splits=args.folds, shuffle=True, random_state=args.seed)
    for name, features in models.items():
        scores = []
        for fold, (train_idx, test_idx) in enumerate(splitter.split(data), start=1):
            score = fold_score(data.iloc[train_idx], data.iloc[test_idx], features)
            scores.append(score)
            rows.append({"model": name, "fold": fold, "c_index": score})
        rows.append({"model": name, "fold": "mean", "c_index": float(np.mean(scores))})
        rows.append({"model": name, "fold": "std", "c_index": float(np.std(scores, ddof=1))})
    output = ROOT / "results" / "radiomics_model_comparison.csv"
    pd.DataFrame(rows).to_csv(output, index=False)
    print(f"Matched cohort: {len(data)} patients. Wrote {output}")


if __name__ == "__main__":
    main()
