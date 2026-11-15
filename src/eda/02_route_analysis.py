
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


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
routes = pd.read_csv(RAW_DIR / "routes.csv")
stops = pd.read_csv(RAW_DIR / "stops.csv")
route_stops = pd.read_csv(RAW_DIR / "route_stops.csv")

print("\n========== CAMPUSFLOW ROUTE ANALYSIS ==========\n")

print("Datasets loaded successfully.")

print(f"Total trips: {len(trips):,}")
print(f"Total routes: {len(routes)}")
print(f"Total stops: {len(stops)}")


# ==================================================
# 3. PREPARE DATA
# ==================================================

# Convert numerical columns
numeric_columns = [
    "passenger_count",
    "available_seats",
    "occupancy_rate",
    "duration_minutes",
    "distance_km"
]

for column in numeric_columns:
    trips[column] = pd.to_numeric(
        trips[column],
        errors="coerce"
    )

# Attach route names to trip records
trip_data = trips.merge(
    routes[["route_id", "route_name"]],
    on="route_id",
    how="left",
    validate="many_to_one"
)

if trip_data["route_name"].isna().any():
    raise ValueError("Some trips have no matching route name.")


# ==================================================
# 4. ROUTE-WISE AGGREGATION
# ==================================================

route_summary = (
    trip_data
    .groupby(["route_id", "route_name"])
    .agg(
        total_trips=("trip_id", "count"),
        total_passengers=("passenger_count", "sum"),
        average_passengers=("passenger_count", "mean"),
        average_occupancy=("occupancy_rate", "mean"),
        average_duration=("duration_minutes", "mean"),
        average_distance=("distance_km", "mean"),
        buses_used=("bus_id", "nunique")
    )
    .reset_index()
)

# Round numerical results
round_columns = [
    "average_passengers",
    "average_occupancy",
    "average_duration",
    "average_distance"
]

route_summary[round_columns] = (
    route_summary[round_columns].round(2)
)

# Sort by total passenger demand
route_summary = route_summary.sort_values(
    by="total_passengers",
    ascending=False
)

route_summary.to_csv(
    SUMMARY_DIR / "route_summary.csv",
    index=False
)


# ==================================================
# 5. ROUTE STOP INFORMATION
# ==================================================

# Count how many stops belong to each route
route_stop_summary = (
    route_stops
    .groupby("route_id")
    .agg(
        number_of_stops=("stop_id", "nunique")
    )
    .reset_index()
)

route_stop_summary = route_stop_summary.merge(
    routes[["route_id", "route_name"]],
    on="route_id",
    how="left",
    validate="one_to_one"
)

route_stop_summary.to_csv(
    SUMMARY_DIR / "route_stop_summary.csv",
    index=False
)


# ==================================================
# 6. STOP USAGE ANALYSIS
# ==================================================

# Count source-stop usage
source_usage = (
    trips["source_stop"]
    .value_counts()
    .rename("origin_trips")
)

# Count destination-stop usage
destination_usage = (
    trips["destination_stop"]
    .value_counts()
    .rename("destination_trips")
)

# Combine both counts
stop_usage = pd.concat(
    [source_usage, destination_usage],
    axis=1
).fillna(0)

stop_usage["total_stop_usage"] = (
    stop_usage["origin_trips"]
    + stop_usage["destination_trips"]
)

stop_usage = (
    stop_usage
    .reset_index()
    .rename(columns={"index": "stop_id"})
)

# Add human-readable stop names
stop_usage = stop_usage.merge(
    stops[["stop_id", "stop_name"]],
    on="stop_id",
    how="left",
    validate="one_to_one"
)

stop_usage = stop_usage.sort_values(
    by="total_stop_usage",
    ascending=False
)

stop_usage.to_csv(
    SUMMARY_DIR / "stop_usage_summary.csv",
    index=False
)


# ==================================================
# 7. CHART 1: TRIPS PER ROUTE
# ==================================================

plt.figure(figsize=(9, 6))

plt.bar(
    route_summary["route_name"],
    route_summary["total_trips"],
    edgecolor="black"
)

plt.title("Total Trips by Route")
plt.xlabel("Bus Route")
plt.ylabel("Number of Trips")
plt.xticks(rotation=15)
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "03_route_trip_volume.png",
    dpi=150
)

plt.close()


# ==================================================
# 8. CHART 2: TOTAL PASSENGERS BY ROUTE
# ==================================================

plt.figure(figsize=(9, 6))

plt.bar(
    route_summary["route_name"],
    route_summary["total_passengers"],
    edgecolor="black"
)

plt.title("Total Passenger Demand by Route")
plt.xlabel("Bus Route")
plt.ylabel("Total Passengers")
plt.xticks(rotation=15)
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "04_route_passenger_demand.png",
    dpi=150
)

plt.close()


# ==================================================
# 9. CHART 3: AVERAGE OCCUPANCY BY ROUTE
# ==================================================

plt.figure(figsize=(9, 6))

plt.bar(
    route_summary["route_name"],
    route_summary["average_occupancy"] * 100,
    edgecolor="black"
)

plt.title("Average Bus Occupancy by Route")
plt.xlabel("Bus Route")
plt.ylabel("Average Occupancy (%)")
plt.xticks(rotation=15)
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "05_route_average_occupancy.png",
    dpi=150
)

plt.close()


# ==================================================
# 10. CHART 4: MOST USED CAMPUS STOPS
# ==================================================

top_stops = stop_usage.head(12)

plt.figure(figsize=(11, 6))

plt.bar(
    top_stops["stop_name"].fillna(top_stops["stop_id"]),
    top_stops["total_stop_usage"],
    edgecolor="black"
)

plt.title("Campus Stop Usage")
plt.xlabel("Campus Stops")
plt.ylabel("Number of Origin and Destination Trips")
plt.xticks(rotation=35, ha="right")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "06_campus_stop_usage.png",
    dpi=150
)

plt.close()


# ==================================================
# 11. GENERATE ANALYSIS REPORT
# ==================================================

highest_trip_route = route_summary.loc[
    route_summary["total_trips"].idxmax()
]

highest_demand_route = route_summary.loc[
    route_summary["total_passengers"].idxmax()
]

highest_occupancy_route = route_summary.loc[
    route_summary["average_occupancy"].idxmax()
]

most_used_stop = stop_usage.iloc[0]

report = f"""# CampusFlow - EDA 2: Route Analysis

**Dataset:** Synthetic campus transportation data

## 1. Route-wise analysis

{route_summary.to_markdown(index=False)}

## 2. Route with the most trips

- Route: {highest_trip_route['route_name']}
- Total trips: {highest_trip_route['total_trips']}

## 3. Route with the highest total passenger demand

- Route: {highest_demand_route['route_name']}
- Total passengers: {highest_demand_route['total_passengers']}

## 4. Route with the highest average occupancy

- Route: {highest_occupancy_route['route_name']}
- Average occupancy: {highest_occupancy_route['average_occupancy']:.2%}

## 5. Most frequently used stop

- Stop: {most_used_stop['stop_name']}
- Total origin and destination trip references:
  {most_used_stop['total_stop_usage']}

## 6. Generated visualizations

1. charts/03_route_trip_volume.png
2. charts/04_route_passenger_demand.png
3. charts/05_route_average_occupancy.png
4. charts/06_campus_stop_usage.png

## 7. Generated summaries

1. summaries/route_summary.csv
2. summaries/route_stop_summary.csv
3. summaries/stop_usage_summary.csv

## 8. Interpretation

The route summaries compare trip volume, total passenger demand,
average passenger count, occupancy, duration and distance.

Stop usage counts how often each stop appears as a trip origin
or destination. It does not measure the number of individual
passengers at that stop.

All results are based on synthetic data and do not represent
actual university transportation activity.
"""

(OUTPUT_DIR / "02_route_analysis_report.md").write_text(
    report,
    encoding="utf-8"
)


# ==================================================
# 12. DISPLAY RESULTS
# ==================================================

print("\n========== ROUTE SUMMARY ==========\n")

print(route_summary.to_string(index=False))

print("\n========== MOST USED STOPS ==========\n")

print(stop_usage.head(12).to_string(index=False))

print("\n========== KEY FINDINGS ==========")

print(
    "\nHighest trip volume:",
    highest_trip_route["route_name"]
)

print(
    "Highest total passenger demand:",
    highest_demand_route["route_name"]
)

print(
    "Highest average occupancy:",
    highest_occupancy_route["route_name"]
)

print(
    "Most used stop:",
    most_used_stop["stop_name"]
)

print("\nAll analysis files saved successfully.")
print(f"Output directory: {OUTPUT_DIR}")

print("\nPhase 1B - EDA 2 completed successfully!")
