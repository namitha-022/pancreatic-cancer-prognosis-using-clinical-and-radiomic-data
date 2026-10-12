"""Pre-planned improvement of the radiomics comparison (run AFTER 01b and 02).

Changes versus 02_compare_survival_models.py (all fixed in advance, nothing tuned on results):
  1. Repeated 5-fold CV (20 repeats = 100 held-out folds) -> stable averages.
  2. Feature selection INSIDE each training fold: keep the top K radiomic features
     ranked by univariate C-index on the training patients only (K = 3).
  3. Standardise features with training-fold statistics, ridge-penalised Cox (penalty 0.5).
  4. Baseline (all 25 features, same repeats) is reported next to the improved model.

Run from the repo root:   python src/radiomics/03_radiomics_improved.py
Output: results/radiomics_improved_comparison.csv  (+ printed table)
"""
from __future__ import annotations

import argparse
import importlib.util
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index
from sklearn.model_selection import RepeatedKFold

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[2]

# Reuse the exact data handling of script 02 (file name starts with a digit -> load by path).
spec = importlib.util.spec_from_file_location("cmp02", Path(__file__).with_name("02_compare_survival_models.py"))
cmp02 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cmp02)
ID, TIME, EVENT = cmp02.ID, cmp02.TIME, cmp02.EVENT


def select_top_k(train: pd.DataFrame, cols: list[str], k: int) -> list[str]:
    scores = {}
    for c in cols:
        x = train[c].fillna(train[c].median())
        if x.nunique() < 2:
            continue
        scores[c] = abs(concordance_index(train[TIME], x, train[EVENT]) - 0.5)
    return sorted(scores, key=scores.get, reverse=True)[:k]


def zscore(train: pd.DataFrame, test: pd.DataFrame, cols: list[str]):
    mu, sd = train[cols].mean(), train[cols].std().replace(0, 1)
    tr, te = train.copy(), test.copy()
    tr[cols], te[cols] = (train[cols] - mu) / sd, (test[cols] - mu) / sd
    return tr, te


def score(train, test, features, penalizer):
    train_x, test_x = cmp02.design_matrix(train, test, features)
    frame = pd.concat([train[[TIME, EVENT]].reset_index(drop=True), train_x.reset_index(drop=True)], axis=1)
    cph = CoxPHFitter(penalizer=penalizer, l1_ratio=0.0)
    cph.fit(frame, duration_col=TIME, event_col=EVENT)
    risk = cph.predict_partial_hazard(test_x).to_numpy().ravel()
    return concordance_index(test[TIME], -risk, test[EVENT])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--radiomics", type=Path, default=ROOT / "data/processed/radiomics_features.csv")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--repeats", type=int, default=20)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    clinical = pd.read_csv(ROOT / "data/processed/clinical_survival_clean.csv")
    radiomics = pd.read_csv(args.radiomics)
    rad_cols = [c for c in radiomics.columns if c != ID and pd.api.types.is_numeric_dtype(radiomics[c])]
    data = clinical.merge(radiomics[[ID] + rad_cols], on=ID, how="inner").dropna(subset=[TIME, EVENT]).reset_index(drop=True)
    drop = {ID, TIME, EVENT, "survival_time_months", "Days to Death", "Days to Last Follow Up", "Vital Status", "Age at Diagnosis"}
    clin_cols = [c for c in clinical.columns if c not in drop and data[c].notna().any()]
    print(f"Matched cohort: {len(data)} patients, {len(rad_cols)} radiomic features, K = {args.k}")

    rkf = RepeatedKFold(n_splits=5, n_repeats=args.repeats, random_state=args.seed)
    names = ["clinical", "radiomics_all25", "combined_all25", f"radiomics_top{args.k}", f"combined_top{args.k}"]
    per_repeat = {n: [[] for _ in range(args.repeats)] for n in names}
    picked = {}
    for i, (tr_idx, te_idx) in enumerate(rkf.split(data)):
        rep = i // 5
        tr, te = data.iloc[tr_idx], data.iloc[te_idx]
        tr_z, te_z = zscore(tr, te, rad_cols)
        top = select_top_k(tr, rad_cols, args.k)
        for f in top:
            picked[f] = picked.get(f, 0) + 1
        jobs = {
            "clinical": (clin_cols, 0.2, False),
            "radiomics_all25": (rad_cols, 0.2, True),
            "combined_all25": (clin_cols + rad_cols, 0.2, True),
            f"radiomics_top{args.k}": (top, 0.5, True),
            f"combined_top{args.k}": (clin_cols + top, 0.5, True),
        }
        for name, (feats, pen, use_z) in jobs.items():
            try:
                s = score(tr_z if use_z else tr, te_z if use_z else te, feats, pen)
                per_repeat[name][rep].append(s)
            except Exception:
                pass

    rows = []
    means = {}
    for n in names:
        reps = np.array([np.mean(r) for r in per_repeat[n] if r])
        means[n] = reps
        rows.append({"model": n, "mean_c_index": reps.mean(), "std_across_repeats": reps.std(ddof=1),
                     "repeat_p2.5": np.percentile(reps, 2.5), "repeat_p97.5": np.percentile(reps, 97.5)})
    out = pd.DataFrame(rows)
    top_name, clin = f"combined_top{args.k}", means["clinical"]
    n = min(len(means[top_name]), len(clin))
    wins = float((means[top_name][:n] > clin[:n]).mean())
    out.to_csv(ROOT / "results" / "radiomics_improved_comparison.csv", index=False)
    print(out.round(3).to_string(index=False))
    print(f"\nShare of repeats where {top_name} beats clinical-only: {wins:.0%}")
    print("Most often selected features:", sorted(picked.items(), key=lambda kv: -kv[1])[:5])
    print("Saved results/radiomics_improved_comparison.csv")


if __name__ == "__main__":
    main()
