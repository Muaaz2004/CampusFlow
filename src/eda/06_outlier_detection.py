
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# CAMPUSFLOW - EDA 6
# OUTLIER DETECTION AND DATA QUALITY ANALYSIS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRIPS_FILE = PROJECT_ROOT / "data" / "raw" / "trips.csv"

REPORT_DIR = PROJECT_ROOT / "reports" / "eda"
CHART_DIR = REPORT_DIR / "charts"
SUMMARY_DIR = REPORT_DIR / "summaries"

CHART_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n========== OUTLIER DETECTION ANALYSIS ==========\n")

df = pd.read_csv(TRIPS_FILE)

print("Total records:", len(df))


# ============================================================
# 2. SELECT NUMERICAL COLUMNS
# ============================================================

columns = [
    "passenger_count",
    "distance_km",
    "duration_minutes",
    "temperature_c",
    "rainfall_mm",
    "available_seats"
]

data = df[columns].copy()

# Convert selected columns to numeric safely.
for column in columns:
    data[column] = pd.to_numeric(
        data[column],
        errors="coerce"
    )


# ============================================================
# 3. DATA QUALITY CHECKS
# ============================================================

print("\n========== DATA QUALITY CHECKS ==========\n")

missing_values = data.isnull().sum()
duplicate_records = df.duplicated().sum()

print("Missing values:")
print(missing_values)

print("\nDuplicate records:", duplicate_records)

quality_summary = pd.DataFrame({
    "column": columns,
    "missing_values": [
        data[column].isnull().sum()
        for column in columns
    ],
    "minimum": [
        data[column].min()
        for column in columns
    ],
    "maximum": [
        data[column].max()
        for column in columns
    ]
})

quality_summary.to_csv(
    SUMMARY_DIR / "data_quality_summary.csv",
    index=False
)


# ============================================================
# 4. IQR OUTLIER DETECTION
# ============================================================

outlier_results = []
outlier_masks = {}

for column in columns:

    values = data[column].dropna()

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    mask = (
        (data[column] < lower_bound) |
        (data[column] > upper_bound)
    )

    outlier_masks[column] = mask

    outlier_count = int(mask.sum())

    outlier_percentage = (
        outlier_count / len(values) * 100
        if len(values) > 0 else 0
    )

    outlier_results.append({
        "feature": column,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "outlier_count": outlier_count,
        "outlier_percentage": outlier_percentage
    })


outlier_summary = pd.DataFrame(outlier_results)

outlier_summary.to_csv(
    SUMMARY_DIR / "outlier_summary.csv",
    index=False
)

print("\n========== OUTLIER SUMMARY ==========\n")

print(
    outlier_summary.to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)


# ============================================================
# 5. SAVE ROWS WITH AT LEAST ONE FLAGGED VALUE
# ============================================================

combined_mask = pd.DataFrame(
    outlier_masks,
    index=data.index
).any(axis=1)

outlier_records = df.loc[combined_mask].copy()

outlier_records.to_csv(
    SUMMARY_DIR / "potential_outlier_records.csv",
    index=False
)

print("\nRecords with at least one flagged feature:",
      len(outlier_records))


# ============================================================
# 6. GENERATE BOXPLOTS
# ============================================================

for column in columns:

    plt.figure(figsize=(9, 5))

    sns.boxplot(
        x=data[column],
        color="skyblue"
    )

    plt.title(f"Outlier Detection - {column}")
    plt.xlabel(column)

    plt.tight_layout()

    filename = (
        "21_boxplot_" + column + ".png"
    )

    plt.savefig(
        CHART_DIR / filename,
        dpi=300
    )

    plt.close()


# ============================================================
# 7. CREATE OUTLIER REPORT
# ============================================================

report = f"""# CampusFlow - EDA 6
## Outlier Detection and Data Quality Analysis

### Dataset Information

- Total records: {len(df)}
- Duplicate records: {duplicate_records}
- Features analysed: {len(columns)}
- Detection method: Interquartile Range (IQR)

### Data Quality Summary

{quality_summary.to_markdown(index=False)}

### Outlier Summary

{outlier_summary.to_markdown(index=False)}

### Important Interpretation

The IQR method flags observations outside:

- Lower bound = Q1 - 1.5 * IQR
- Upper bound = Q3 + 1.5 * IQR

A flagged observation is not automatically an error.

For example, high rainfall or high passenger demand
may be valid observations.

Outliers must be investigated before deciding whether
to retain, transform, or remove them.

### Important Project Note

CampusFlow uses synthetic data.

The results describe the generated simulation and
should not be interpreted as actual campus transport data.
"""

REPORT_FILE = (
    REPORT_DIR / "06_outlier_detection_report.md"
)

REPORT_FILE.write_text(
    report,
    encoding="utf-8"
)


# ============================================================
# 8. COMPLETION
# ============================================================

print("\n========== ANALYSIS COMPLETED ==========\n")

print("Data quality report saved.")
print("Outlier summary saved.")
print("Potential outlier records saved.")
print("Boxplots generated.")

print("\nCharts directory:", CHART_DIR)
print("Summary directory:", SUMMARY_DIR)
print("Report:", REPORT_FILE)

print("\nPhase 1B - EDA 6 completed successfully!")
