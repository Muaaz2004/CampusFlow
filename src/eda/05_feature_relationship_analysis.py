
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# CAMPUSFLOW - EDA 5
# FEATURE RELATIONSHIP AND CORRELATION ANALYSIS
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

print("\n========== FEATURE RELATIONSHIP ANALYSIS ==========\n")

trips = pd.read_csv(TRIPS_FILE)

print("Dataset loaded successfully.")
print("Total records:", len(trips))


# ============================================================
# 2. SELECT NUMERICAL FEATURES
# ============================================================

target = "passenger_count"

features = [
    "distance_km",
    "duration_minutes",
    "temperature_c",
    "rainfall_mm",
    "hour",
    "day_of_week",
    "is_weekend",
    "is_exam_day",
    "is_event_day",
    "available_seats"
]

analysis_columns = features + [target]

# Select only required numerical columns.
analysis_data = trips[analysis_columns].copy()

# Handle missing values for correlation analysis.
analysis_data = analysis_data.dropna()

print("Valid records:", len(analysis_data))
print("Features selected:", len(features))


# ============================================================
# 3. CORRELATION MATRIX
# ============================================================

correlation_matrix = analysis_data.corr(
    method="pearson"
)

# Save the complete correlation matrix.
correlation_matrix.to_csv(
    SUMMARY_DIR / "feature_correlation_matrix.csv"
)

# Extract correlations against passenger_count.
target_correlation = (
    correlation_matrix[target]
    .drop(target)
    .sort_values(ascending=False)
)

correlation_summary = pd.DataFrame({
    "feature": target_correlation.index,
    "correlation_with_passenger_count": target_correlation.values
})

correlation_summary.to_csv(
    SUMMARY_DIR / "feature_target_correlation.csv",
    index=False
)

print("\n========== CORRELATION WITH PASSENGER COUNT ==========\n")
print(correlation_summary.to_string(index=False))


# ============================================================
# 4. CORRELATION HEATMAP
# ============================================================

plt.figure(figsize=(13, 9))

sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap="coolwarm",
    center=0,
    fmt=".2f",
    linewidths=0.5
)

plt.title("CampusFlow Feature Correlation Heatmap")
plt.tight_layout()

plt.savefig(
    CHART_DIR / "16_feature_correlation_heatmap.png",
    dpi=300
)

plt.close()


# ============================================================
# 5. PASSENGER COUNT VS DISTANCE
# ============================================================

plt.figure(figsize=(9, 6))

sns.scatterplot(
    data=analysis_data,
    x="distance_km",
    y="passenger_count",
    alpha=0.3
)

plt.title("Passenger Count vs Trip Distance")
plt.xlabel("Trip Distance (km)")
plt.ylabel("Number of Passengers")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "17_passengers_vs_distance.png",
    dpi=300
)

plt.close()


# ============================================================
# 6. PASSENGER COUNT VS DURATION
# ============================================================

plt.figure(figsize=(9, 6))

sns.scatterplot(
    data=analysis_data,
    x="duration_minutes",
    y="passenger_count",
    alpha=0.3
)

plt.title("Passenger Count vs Trip Duration")
plt.xlabel("Trip Duration (minutes)")
plt.ylabel("Number of Passengers")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "18_passengers_vs_duration.png",
    dpi=300
)

plt.close()


# ============================================================
# 7. PASSENGER COUNT VS TEMPERATURE
# ============================================================

plt.figure(figsize=(9, 6))

sns.scatterplot(
    data=analysis_data,
    x="temperature_c",
    y="passenger_count",
    alpha=0.3
)

plt.title("Passenger Count vs Temperature")
plt.xlabel("Temperature (Celsius)")
plt.ylabel("Number of Passengers")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "19_passengers_vs_temperature.png",
    dpi=300
)

plt.close()


# ============================================================
# 8. PASSENGER COUNT VS RAINFALL
# ============================================================

plt.figure(figsize=(9, 6))

sns.scatterplot(
    data=analysis_data,
    x="rainfall_mm",
    y="passenger_count",
    alpha=0.3
)

plt.title("Passenger Count vs Rainfall")
plt.xlabel("Rainfall (mm)")
plt.ylabel("Number of Passengers")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "20_passengers_vs_rainfall.png",
    dpi=300
)

plt.close()


# ============================================================
# 9. FIND STRONGEST POSITIVE AND NEGATIVE RELATIONSHIPS
# ============================================================

strongest_positive = target_correlation.idxmax()
strongest_negative = target_correlation.idxmin()

positive_value = target_correlation.max()
negative_value = target_correlation.min()

print("\n========== KEY FINDINGS ==========\n")

print(
    f"Strongest positive relationship: "
    f"{strongest_positive} ({positive_value:.4f})"
)

print(
    f"Strongest negative relationship: "
    f"{strongest_negative} ({negative_value:.4f})"
)


# ============================================================
# 10. GENERATE MARKDOWN REPORT
# ============================================================

report = f"""# CampusFlow - EDA 5
## Feature Relationship and Correlation Analysis

### Dataset Information

- Total records analysed: {len(analysis_data)}
- Target variable: passenger_count
- Numerical features analysed: {len(features)}
- Correlation method: Pearson correlation

### Correlation with Passenger Count

{correlation_summary.to_markdown(index=False)}

### Key Findings

- Strongest positive relationship: {strongest_positive}
  (correlation: {positive_value:.4f})

- Strongest negative relationship: {strongest_negative}
  (correlation: {negative_value:.4f})

### Important Interpretation

Pearson correlation measures the strength and direction
of a linear relationship between two numerical variables.

A positive correlation means that the variables tend to
increase together.

A negative correlation means that one variable tends
to decrease when the other increases.

A correlation close to zero indicates a weak linear
relationship. It does not rule out nonlinear relationships.

### Machine Learning Considerations

The target variable is passenger_count.

The following features were excluded:

- occupancy_rate: directly derived from passenger_count
  and available_seats, so it would introduce target leakage.
- trip_id, bus_id and route_id: identifiers are not treated
  as numerical measurements in this correlation analysis.

Correlation does not prove causation.

All CampusFlow observations are synthetic and represent
a simulated campus transportation environment.
"""

REPORT_FILE = REPORT_DIR / "05_feature_relationship_report.md"

REPORT_FILE.write_text(
    report,
    encoding="utf-8"
)


# ============================================================
# 11. COMPLETION
# ============================================================

print("\n========== ANALYSIS COMPLETED ==========\n")

print("Strongest positive feature:", strongest_positive)
print("Strongest negative feature:", strongest_negative)

print("\nCharts saved inside:")
print(CHART_DIR)

print("\nSummary files saved inside:")
print(SUMMARY_DIR)

print("\nReport saved:", REPORT_FILE)

print("\nPhase 1B - EDA 5 completed successfully!")
