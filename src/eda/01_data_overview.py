
from pathlib import Path
import json

import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"

OUTPUT_DIR = PROJECT_ROOT / "reports" / "eda"
CHART_DIR = OUTPUT_DIR / "charts"
SUMMARY_DIR = OUTPUT_DIR / "summaries"

for folder in [OUTPUT_DIR, CHART_DIR, SUMMARY_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOAD DATASETS
# --------------------------------------------------

csv_files = [
    "stops.csv",
    "routes.csv",
    "route_stops.csv",
    "weather.csv",
    "trips.csv"
]

datasets = {}

print("\n========== CAMPUSFLOW DATA OVERVIEW ==========\n")

for filename in csv_files:
    file_path = RAW_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(file_path)
    datasets[filename] = df

    print(f"{filename}")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print("-" * 45)


# --------------------------------------------------
# 3. LOAD STREAMING EVENTS
# --------------------------------------------------

events_path = RAW_DIR / "boarding_events.jsonl"

if not events_path.exists():
    raise FileNotFoundError(f"Dataset not found: {events_path}")

with events_path.open("r", encoding="utf-8") as file:
    event_count = sum(1 for line in file if line.strip())

print(f"boarding_events.jsonl")
print(f"Records: {event_count}")
print("-" * 45)


# --------------------------------------------------
# 4. TRIP DATA ANALYSIS
# --------------------------------------------------

trips = datasets["trips.csv"].copy()

# Convert date column into datetime format
trips["travel_date"] = pd.to_datetime(
    trips["travel_date"],
    errors="coerce"
)

# Convert important columns into numeric format
numeric_columns = [
    "hour",
    "day_of_week",
    "passenger_count",
    "available_seats",
    "occupancy_rate",
    "duration_minutes",
    "distance_km",
    "temperature_c",
    "rainfall_mm"
]

for column in numeric_columns:
    trips[column] = pd.to_numeric(
        trips[column],
        errors="coerce"
    )


# --------------------------------------------------
# 5. DATASET PROFILE
# --------------------------------------------------

profile_rows = []

for filename, df in datasets.items():

    for column in df.columns:

        profile_rows.append({
            "dataset": filename,
            "column": column,
            "data_type": str(df[column].dtype),
            "total_records": len(df),
            "missing_values": int(df[column].isna().sum()),
            "unique_values": int(df[column].nunique())
        })

profile = pd.DataFrame(profile_rows)

profile.to_csv(
    SUMMARY_DIR / "dataset_profile.csv",
    index=False
)


# --------------------------------------------------
# 6. DATA QUALITY ANALYSIS
# --------------------------------------------------

quality_checks = []

for filename, df in datasets.items():

    quality_checks.append({
        "dataset": filename,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum())
    })


# Check unique trip IDs
duplicate_trip_ids = int(
    trips["trip_id"].duplicated().sum()
)

quality_checks.append({
    "dataset": "trips.csv - trip_id check",
    "total_rows": len(trips),
    "total_columns": len(trips.columns),
    "missing_cells": int(trips["trip_id"].isna().sum()),
    "duplicate_rows": duplicate_trip_ids
})

quality_report = pd.DataFrame(quality_checks)

quality_report.to_csv(
    SUMMARY_DIR / "data_quality_report.csv",
    index=False
)


# --------------------------------------------------
# 7. NUMERICAL STATISTICS
# --------------------------------------------------

statistics = trips[numeric_columns].describe().T

statistics.to_csv(
    SUMMARY_DIR / "trip_statistics.csv"
)


# --------------------------------------------------
# 8. CHART 1: PASSENGER COUNT DISTRIBUTION
# --------------------------------------------------

plt.figure(figsize=(10, 6))

plt.hist(
    trips["passenger_count"].dropna(),
    bins=20,
    edgecolor="black"
)

plt.title("Distribution of Passenger Counts")
plt.xlabel("Number of Passengers")
plt.ylabel("Number of Trips")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "01_passenger_distribution.png",
    dpi=150
)

plt.close()


# --------------------------------------------------
# 9. CHART 2: MONTHLY TRIP VOLUME
# --------------------------------------------------

monthly_trips = (
    trips.dropna(subset=["travel_date"])
    .set_index("travel_date")
    .resample("MS")
    .size()
)

plt.figure(figsize=(12, 6))

monthly_trips.plot(
    marker="o",
    linewidth=2
)

plt.title("Monthly Campus Shuttle Trip Volume")
plt.xlabel("Month")
plt.ylabel("Number of Trips")
plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "02_monthly_trip_volume.png",
    dpi=150
)

plt.close()


# --------------------------------------------------
# 10. GENERATE MARKDOWN REPORT
# --------------------------------------------------

total_trips = len(trips)

average_passengers = trips["passenger_count"].mean()
maximum_passengers = trips["passenger_count"].max()
minimum_passengers = trips["passenger_count"].min()

average_occupancy = trips["occupancy_rate"].mean()

date_min = trips["travel_date"].min()
date_max = trips["travel_date"].max()

total_missing = int(trips.isna().sum().sum())

report = f"""# CampusFlow - EDA 1: Data Overview

**Dataset type:** Synthetic / Fictional campus transportation data

## 1. Dataset information

- Total historical trips: {total_trips:,}
- Total streaming events: {event_count:,}
- Trip date range: {date_min} to {date_max}

## 2. Passenger statistics

- Average passengers per trip: {average_passengers:.2f}
- Maximum passengers in a trip: {maximum_passengers}
- Minimum passengers in a trip: {minimum_passengers}
- Average occupancy rate: {average_occupancy:.4f}

## 3. Data quality

- Missing values in trips dataset: {total_missing}
- Duplicate trip IDs: {duplicate_trip_ids}

## 4. Generated visualizations

1. charts/01_passenger_distribution.png
2. charts/02_monthly_trip_volume.png

## 5. Generated summary files

1. summaries/dataset_profile.csv
2. summaries/data_quality_report.csv
3. summaries/trip_statistics.csv

## 6. Interpretation

The passenger distribution chart shows how passenger counts
are distributed across historical trips.

The monthly trip chart shows how trip volume varies across
the simulated year.

These results describe a synthetic transportation environment
and should not be interpreted as real university ridership.

## 7. Next step

Proceed to detailed temporal, route, weather, occupancy,
stop and streaming-event analysis.
"""

(OUTPUT_DIR / "01_data_overview_report.md").write_text(
    report,
    encoding="utf-8"
)


# --------------------------------------------------
# 11. FINAL OUTPUT
# --------------------------------------------------

print("\n========== ANALYSIS COMPLETED ==========")

print(f"Total trips: {total_trips:,}")
print(f"Average passengers: {average_passengers:.2f}")
print(f"Average occupancy: {average_occupancy:.4f}")
print(f"Duplicate trip IDs: {duplicate_trip_ids}")

print("\nFiles saved inside:")
print(OUTPUT_DIR)

print("\nPhase 1B - EDA 1 completed successfully!")
