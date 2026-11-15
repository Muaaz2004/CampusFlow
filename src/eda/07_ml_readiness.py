
from pathlib import Path
import json
import pandas as pd

# --------------------------------------------------
# CAMPUSFLOW - EDA 7: MACHINE LEARNING READINESS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "trips.csv"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "eda"
SUMMARY_DIR = OUTPUT_DIR / "summaries"

SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "passenger_count"

print("\n========== CAMPUSFLOW ML READINESS ANALYSIS ==========\n")

# 1. LOAD DATA
df = pd.read_csv(INPUT_FILE)

print("Dataset loaded successfully.")
print("Total records:", len(df))
print("Total columns:", len(df.columns))

# 2. REQUIRED COLUMN VALIDATION
required_columns = [
    "travel_date", "passenger_count", "route_id",
    "hour", "day_of_week", "is_weekend",
    "season", "weather", "temperature_c",
    "rainfall_mm", "is_exam_day", "is_event_day",
    "source_stop", "destination_stop", "distance_km"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# 3. CHECK TARGET
df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
df["travel_date"] = pd.to_datetime(
    df["travel_date"], errors="coerce"
)

if df[TARGET].isna().any():
    raise ValueError("Target contains missing or invalid values.")

if df["travel_date"].isna().any():
    raise ValueError("Some travel_date values could not be parsed.")

# 4. CHECK AVAILABLE_SEATS SEMANTICS
# Include it only if it is stable for each bus.
capacity_feature = False

if "available_seats" in df.columns and "bus_id" in df.columns:
    seats_per_bus = df.groupby("bus_id")["available_seats"].nunique()

    if (seats_per_bus == 1).all():
        capacity_feature = True
        df = df.rename(
            columns={"available_seats": "bus_capacity_seats"}
        )
        print("\nAvailable seats check: stable per bus.")
        print("Treating this field as bus capacity.")
    else:
        print("\nAvailable seats check: values change per bus.")
        print("Excluding it because its meaning may involve")
        print("remaining seats or post-boarding information.")
else:
    print("\nAvailable seats field unavailable.")

# 5. SELECT FEATURES
numerical_features = [
    "hour",
    "day_of_week",
    "is_weekend",
    "temperature_c",
    "rainfall_mm",
    "is_exam_day",
    "is_event_day",
    "distance_km"
]

categorical_features = [
    "route_id",
    "season",
    "weather",
    "source_stop",
    "destination_stop"
]

if capacity_feature:
    numerical_features.append("bus_capacity_seats")

selected_features = numerical_features + categorical_features

# Verify all selected columns exist
selected_features = [
    col for col in selected_features if col in df.columns
]

# 6. EXPLICITLY EXCLUDED COLUMNS
excluded_features = {
    "trip_id": "Unique identifier; not a useful predictor.",
    "bus_id": "Vehicle identifier; capacity is represented separately if verified.",
    "travel_date": "Used for chronological splitting, not directly as a feature.",
    "departure_time": "Hour is already represented by the hour column.",
    "arrival_time": "Post-trip information; unavailable before prediction.",
    "day_name": "Redundant with day_of_week.",
    "occupancy_rate": "Target leakage: calculated using passenger_count.",
    "duration_minutes": "Post-trip information; unavailable before departure.",
    "passenger_count": "Prediction target, not an input feature."
}

if not capacity_feature:
    excluded_features["available_seats"] = (
        "Meaning is not confirmed or values vary per bus."
    )

# 7. FEATURE AUDIT REPORT
audit_rows = []

for feature in selected_features:
    dtype = str(df[feature].dtype)

    if feature in numerical_features:
        feature_type = "Numerical"
    else:
        feature_type = "Categorical"

    audit_rows.append({
        "feature": feature,
        "data_type": dtype,
        "feature_category": feature_type,
        "decision": "INCLUDE",
        "reason": "Available before trip prediction."
    })

for feature, reason in excluded_features.items():
    audit_rows.append({
        "feature": feature,
        "data_type": str(df[feature].dtype)
        if feature in df.columns else "Not present",
        "feature_category": "Excluded",
        "decision": "EXCLUDE",
        "reason": reason
    })

audit = pd.DataFrame(audit_rows)

audit.to_csv(
    SUMMARY_DIR / "07_feature_selection_audit.csv",
    index=False
)

# 8. CHECK FEATURE MISSING VALUES
missing_summary = (
    df[selected_features]
    .isnull()
    .sum()
    .to_dict()
)

# 9. CHRONOLOGICAL TRAIN/TEST SPLIT
# Split by distinct dates to prevent trips from the
# same date appearing in both datasets.

unique_dates = sorted(df["travel_date"].dt.date.unique())

if len(unique_dates) < 2:
    raise ValueError("Not enough distinct dates for chronological split.")

split_position = int(len(unique_dates) * 0.80)
split_position = max(1, min(split_position, len(unique_dates) - 1))

split_date = unique_dates[split_position]

train_df = df[df["travel_date"].dt.date < split_date].copy()
test_df = df[df["travel_date"].dt.date >= split_date].copy()

# Keep travel_date for traceability, but do not use it
# as a model input.
output_columns = ["travel_date"] + selected_features + [TARGET]

train_df[output_columns].to_csv(
    SUMMARY_DIR / "07_train_dataset.csv",
    index=False
)

test_df[output_columns].to_csv(
    SUMMARY_DIR / "07_test_dataset.csv",
    index=False
)

# 10. SUMMARY
summary = {
    "project": "CampusFlow",
    "analysis": "EDA 7 - Machine Learning Readiness",
    "total_records": int(len(df)),
    "target": TARGET,
    "problem_type": "Supervised Regression",
    "selected_features": selected_features,
    "numerical_features": numerical_features,
    "categorical_features": categorical_features,
    "excluded_features": excluded_features,
    "available_seats_treated_as_capacity": capacity_feature,
    "feature_missing_values": missing_summary,
    "split_method": "Chronological 80/20 by distinct travel dates",
    "split_date": str(split_date),
    "training_records": int(len(train_df)),
    "testing_records": int(len(test_df)),
    "training_start": str(train_df["travel_date"].min().date()),
    "training_end": str(train_df["travel_date"].max().date()),
    "testing_start": str(test_df["travel_date"].min().date()),
    "testing_end": str(test_df["travel_date"].max().date()),
    "target_leakage_excluded": [
        "occupancy_rate",
        "duration_minutes",
        "arrival_time"
    ]
}

with open(
    SUMMARY_DIR / "07_ml_readiness_summary.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(summary, file, indent=4)

# 11. PRINT RESULTS
print("\n========== SELECTED FEATURES ==========")

for feature in selected_features:
    print("-", feature)

print("\nNumerical features:", len(numerical_features))
print("Categorical features:", len(categorical_features))

print("\n========== CHRONOLOGICAL SPLIT ==========")
print("Split date:", split_date)
print("Training records:", len(train_df))
print("Testing records:", len(test_df))

print("\nTraining period:")
print(train_df["travel_date"].min(), "to",
      train_df["travel_date"].max())

print("\nTesting period:")
print(test_df["travel_date"].min(), "to",
      test_df["travel_date"].max())

print("\n========== MISSING VALUE CHECK ==========")
print(pd.Series(missing_summary))

print("\n========== OUTPUT FILES ==========")
print("07_feature_selection_audit.csv")
print("07_train_dataset.csv")
print("07_test_dataset.csv")
print("07_ml_readiness_summary.json")

print("\nPhase 1B - EDA 7 completed successfully!")
