
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ==================================================
# 1. PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"

OUTPUT_DIR = PROJECT_ROOT / "reports" / "eda"
CHART_DIR = OUTPUT_DIR / "charts"
SUMMARY_DIR = OUTPUT_DIR / "summaries"

CHART_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. LOAD DATASETS
# ==================================================

trips = pd.read_csv(RAW_DIR / "trips.csv")
weather = pd.read_csv(RAW_DIR / "weather.csv")

print("\n========== WEATHER AND SEASONAL ANALYSIS ==========\n")

print("Trip records:", len(trips))
print("Daily weather records:", len(weather))


# ==================================================
# 3. DATA PREPARATION
# ==================================================

numeric_columns = [
    "passenger_count",
    "occupancy_rate",
    "temperature_c",
    "rainfall_mm",
    "hour",
    "is_exam_day",
    "is_event_day"
]

for column in numeric_columns:
    trips[column] = pd.to_numeric(
        trips[column],
        errors="coerce"
    )

trips["travel_date"] = pd.to_datetime(
    trips["travel_date"],
    errors="coerce"
)

# Remove records missing the essential fields
analysis_data = trips.dropna(
    subset=[
        "passenger_count",
        "occupancy_rate",
        "season",
        "weather",
        "temperature_c",
        "rainfall_mm",
        "hour"
    ]
).copy()

print("Records available for analysis:", len(analysis_data))


# ==================================================
# 4. SEASONAL DEMAND ANALYSIS
# ==================================================

season_summary = (
    analysis_data
    .groupby("season")
    .agg(
        total_trips=("trip_id", "count"),
        total_passengers=("passenger_count", "sum"),
        average_passengers=("passenger_count", "mean"),
        average_occupancy=("occupancy_rate", "mean"),
        average_temperature=("temperature_c", "mean"),
        average_rainfall=("rainfall_mm", "mean")
    )
    .reset_index()
)

season_summary = season_summary.round(2)

season_summary.to_csv(
    SUMMARY_DIR / "seasonal_demand_summary.csv",
    index=False
)


# ==================================================
# 5. WEATHER CONDITION ANALYSIS
# ==================================================

weather_summary = (
    analysis_data
    .groupby("weather")
    .agg(
        total_trips=("trip_id", "count"),
        total_passengers=("passenger_count", "sum"),
        average_passengers=("passenger_count", "mean"),
        average_occupancy=("occupancy_rate", "mean"),
        average_temperature=("temperature_c", "mean"),
        average_rainfall=("rainfall_mm", "mean")
    )
    .reset_index()
)

weather_summary = weather_summary.round(2)

weather_summary.to_csv(
    SUMMARY_DIR / "weather_demand_summary.csv",
    index=False
)


# ==================================================
# 6. RAINFALL CATEGORY ANALYSIS
# ==================================================

# Define rainfall ranges in millimetres
rainfall_bins = [
    -0.001, 0, 5, 15, float("inf")
]

rainfall_labels = [
    "No Rain",
    "Light Rain",
    "Moderate Rain",
    "Heavy Rain"
]

analysis_data["rainfall_category"] = pd.cut(
    analysis_data["rainfall_mm"],
    bins=rainfall_bins,
    labels=rainfall_labels
)

rainfall_summary = (
    analysis_data
    .groupby("rainfall_category", observed=False)
    .agg(
        total_trips=("trip_id", "count"),
        average_passengers=("passenger_count", "mean"),
        average_occupancy=("occupancy_rate", "mean"),
        average_temperature=("temperature_c", "mean")
    )
    .reset_index()
)

rainfall_summary = rainfall_summary.round(2)

rainfall_summary.to_csv(
    SUMMARY_DIR / "rainfall_demand_summary.csv",
    index=False
)


# ==================================================
# 7. HOURLY DEMAND UNDER DIFFERENT WEATHER
# ==================================================

hourly_weather = (
    analysis_data
    .pivot_table(
        index="hour",
        columns="weather",
        values="passenger_count",
        aggfunc="mean",
        observed=False
    )
)

hourly_weather.to_csv(
    SUMMARY_DIR / "hourly_weather_demand.csv"
)


# ==================================================
# 8. CHART 1: SEASONAL PASSENGER DEMAND
# ==================================================

plt.figure(figsize=(10, 6))

sns.barplot(
    data=season_summary,
    x="season",
    y="average_passengers"
)

plt.title("Average Passenger Demand by Season")
plt.xlabel("Season")
plt.ylabel("Average Passengers per Trip")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "07_seasonal_passenger_demand.png",
    dpi=150
)

plt.close()


# ==================================================
# 9. CHART 2: WEATHER CONDITION DEMAND
# ==================================================

plt.figure(figsize=(9, 6))

sns.barplot(
    data=weather_summary,
    x="weather",
    y="average_passengers"
)

plt.title("Average Passenger Demand by Weather")
plt.xlabel("Weather Condition")
plt.ylabel("Average Passengers per Trip")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "08_weather_passenger_demand.png",
    dpi=150
)

plt.close()


# ==================================================
# 10. CHART 3: RAINFALL VS PASSENGER DEMAND
# ==================================================

plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=analysis_data,
    x="rainfall_mm",
    y="passenger_count",
    alpha=0.35
)

plt.title("Rainfall vs Passenger Count")
plt.xlabel("Rainfall (mm)")
plt.ylabel("Number of Passengers")
plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "09_rainfall_vs_passengers.png",
    dpi=150
)

plt.close()


# ==================================================
# 11. CHART 4: HOURLY WEATHER HEATMAP
# ==================================================

plt.figure(figsize=(10, 7))

sns.heatmap(
    hourly_weather,
    annot=True,
    fmt=".1f",
    cmap="YlOrRd",
    linewidths=0.5
)

plt.title("Average Passenger Demand by Hour and Weather")
plt.xlabel("Weather Condition")
plt.ylabel("Departure Hour")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "10_hourly_weather_heatmap.png",
    dpi=150
)

plt.close()


# ==================================================
# 12. TEMPERATURE CORRELATION
# ==================================================

temperature_correlation = (
    analysis_data[
        ["temperature_c", "passenger_count"]
    ]
    .corr()
    .iloc[0, 1]
)

rainfall_correlation = (
    analysis_data[
        ["rainfall_mm", "passenger_count"]
    ]
    .corr()
    .iloc[0, 1]
)


# ==================================================
# 13. KEY FINDINGS
# ==================================================

highest_season = season_summary.loc[
    season_summary["average_passengers"].idxmax()
]

lowest_season = season_summary.loc[
    season_summary["average_passengers"].idxmin()
]

highest_weather = weather_summary.loc[
    weather_summary["average_passengers"].idxmax()
]

lowest_weather = weather_summary.loc[
    weather_summary["average_passengers"].idxmin()
]


# ==================================================
# 14. GENERATE MARKDOWN REPORT
# ==================================================

report = f"""# CampusFlow - EDA 3: Weather and Seasonal Analysis

**Dataset:** Synthetic campus transportation data

## 1. Seasonal Demand

{season_summary.to_markdown(index=False)}

Highest average seasonal demand:
- Season: {highest_season['season']}
- Average passengers: {highest_season['average_passengers']}

Lowest average seasonal demand:
- Season: {lowest_season['season']}
- Average passengers: {lowest_season['average_passengers']}

## 2. Weather Condition Analysis

{weather_summary.to_markdown(index=False)}

Highest average demand by weather:
- Condition: {highest_weather['weather']}
- Average passengers: {highest_weather['average_passengers']}

Lowest average demand by weather:
- Condition: {lowest_weather['weather']}
- Average passengers: {lowest_weather['average_passengers']}

## 3. Rainfall Analysis

{rainfall_summary.to_markdown(index=False)}

## 4. Correlation Analysis

- Temperature vs passenger count correlation: {temperature_correlation:.4f}
- Rainfall vs passenger count correlation: {rainfall_correlation:.4f}

Correlation measures linear association, not causation.

## 5. Generated Visualizations

1. charts/07_seasonal_passenger_demand.png
2. charts/08_weather_passenger_demand.png
3. charts/09_rainfall_vs_passengers.png
4. charts/10_hourly_weather_heatmap.png

## 6. Generated Summary Files

1. summaries/seasonal_demand_summary.csv
2. summaries/weather_demand_summary.csv
3. summaries/rainfall_demand_summary.csv
4. summaries/hourly_weather_demand.csv

## 7. Interpretation

The analysis compares passenger demand across seasons,
weather conditions, rainfall categories, and departure hours.

The correlation values indicate the strength and direction
of linear associations in the synthetic dataset.

These observations do not establish that weather causes
changes in passenger demand.

All results describe the simulated CampusFlow environment
and should not be treated as actual university ridership.

"""

(OUTPUT_DIR / "03_weather_seasonal_report.md").write_text(
    report,
    encoding="utf-8"
)


# ==================================================
# 15. DISPLAY RESULTS
# ==================================================

print("\n========== SEASONAL DEMAND ==========\n")
print(season_summary.to_string(index=False))

print("\n========== WEATHER DEMAND ==========\n")
print(weather_summary.to_string(index=False))

print("\n========== RAINFALL ANALYSIS ==========\n")
print(rainfall_summary.to_string(index=False))

print("\n========== CORRELATION RESULTS ==========")

print(
    f"Temperature correlation: {temperature_correlation:.4f}"
)

print(
    f"Rainfall correlation: {rainfall_correlation:.4f}"
)

print("\n========== KEY FINDINGS ==========")

print(
    "Highest demand season:",
    highest_season["season"]
)

print(
    "Lowest demand season:",
    lowest_season["season"]
)

print(
    "Highest demand weather:",
    highest_weather["weather"]
)

print(
    "Lowest demand weather:",
    lowest_weather["weather"]
)

print("\nAll analysis files saved successfully.")
print(f"Output directory: {OUTPUT_DIR}")

print("\nPhase 1B - EDA 3 completed successfully!")
