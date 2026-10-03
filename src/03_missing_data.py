import pandas as pd
from pathlib import Path

INPUT_PATH = Path(
    "data/processed/clinical_survival_clean.csv"
)

OUTPUT_PATH = Path(
    "results/missing_data_report.csv"
)

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df = pd.read_csv(INPUT_PATH)

report = pd.DataFrame({
    "variable": df.columns,
    "missing_count": df.isna().sum(),
    "total": len(df),
})

report["missing_percentage"] = (
    report["missing_count"] /
    report["total"] * 100
)

report = report.sort_values(
    "missing_percentage",
    ascending=False
)

print(report.to_string(index=False))

report.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nSaved:")
print(OUTPUT_PATH)