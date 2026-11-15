
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
# 2. LOAD DATA
# ==================================================

trips = pd.read_csv(RAW_DIR / "trips.csv")

print("\n========== TIME-BASED DEMAND ANALYSIS ==========\n")

print("Total trip records:", len(trips))


# ==================================================
# 3. DATA PREPARATION
# ==================================================

numeric_columns = [
    "hour",
    "day_of_week",
    "is_weekend",
    "is_exam_day",
    "is_event_day",
    "passenger_count",
    "occupancy_rate"
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

analysis_data = trips.dropna(
    subset=[
        "hour",
        "day_of_week",
        "is_weekend",
        "is_exam_day",
        "is_event_day",
        "passenger_count",
        "occupancy_rate",
        "travel_date"
    ]
).copy()

print("Valid records for analysis:", len(analysis_data))


# ==================================================
# 4. HOURLY DEMAND ANALYSIS
# ==================================================

hourly_summary = (
    analysis_data
    .groupby("hour")
    .agg(
        total_trips=("trip_id", "count"),
        total_passengers=("passenger_count", "sum"),
        average_passengers=("passenger_count", "mean"),
        average_occupancy=("occupancy_rate", "mean")
    )
    .reset_index()
    .sort_values("hour")
)

hourly_summary = hourly_summary.round(2)

hourly_summary.to_csv(
    SUMMARY_DIR / "hourly_demand_summary.csv",
    index=False
)


# ==================================================
# 5. DAY-OF-WEEK ANALYSIS
# ==================================================

day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

daily_summary = (
    analysis_data
    .groupby(["day_of_week", "day_name"])
    .agg(
        total_trips=("trip_id", "count"),
        total_passengers=("passenger_count", "sum"),
        average_passengers=("passenger_count", "mean"),
        average_occupancy=("occupancy_rate", "mean")
    )
    .reset_index()
)

daily_summary["day_name"] = pd.Categorical(
    daily_summary["day_name"],
    categories=day_order,
    ordered=True
)

daily_summary = (
    daily_summary
    .sort_values("day_name")
    .round(2)
)

daily_summary.to_csv(
    SUMMARY_DIR / "day_of_week_demand_summary.csv",
    index=False
)


# ==================================================
# 6. WEEKDAY VS WEEKEND ANALYSIS
# ==================================================

analysis_data["day_type"] = (
    analysis_data["is_weekend"]
    .map({
        0: "Weekday",
        1: "Weekend"
    })
)

weekend_summary = (
    analysis_data
    .groupby("day_type")
    .agg(
        total_trips=("trip_id", "count"),
        total_passengers=("passenger_count", "sum"),
        average_passengers=("passenger_count", "mean"),
        average_occupancy=("occupancy_rate", "mean")
    )
    .reset_index()
)

weekend_summary = weekend_summary.round(2)

weekend_summary.to_csv(
    SUMMARY_DIR / "weekday_weekend_summary.csv",
    index=False
)


# ==================================================
# 7. EXAM-DAY ANALYSIS
# ==================================================

analysis_data["exam_category"] = (
    analysis_data["is_exam_day"]
    .map({
        0: "Normal Day",
        1: "Exam Day"
    })
)

exam_summary = (
    analysis_data
    .groupby("exam_category")
    .agg(
        total_trips=("trip_id", "count"),
        total_passengers=("passenger_count", "sum"),
        average_passengers=("passenger_count", "mean"),
        average_occupancy=("occupancy_rate", "mean")
    )
    .reset_index()
)

exam_summary = exam_summary.round(2)

exam_summary.to_csv(
    SUMMARY_DIR / "exam_day_demand_summary.csv",
    index=False
)


# ==================================================
# 8. EVENT-DAY ANALYSIS
# ==================================================

analysis_data["event_category"] = (
    analysis_data["is_event_day"]
    .map({
        0: "Normal Day",
        1: "Event Day"
    })
)

event_summary = (
    analysis_data
    .groupby("event_category")
    .agg(
        total_trips=("trip_id", "count"),
        total_passengers=("passenger_count", "sum"),
        average_passengers=("passenger_count", "mean"),
        average_occupancy=("occupancy_rate", "mean")
    )
    .reset_index()
)

event_summary = event_summary.round(2)

event_summary.to_csv(
    SUMMARY_DIR / "event_day_demand_summary.csv",
    index=False
)


# ==================================================
# 9. CHART 1: HOURLY PASSENGER DEMAND
# ==================================================

plt.figure(figsize=(11, 6))

sns.lineplot(
    data=hourly_summary,
    x="hour",
    y="average_passengers",
    marker="o"
)

plt.title("Average Passenger Demand by Departure Hour")
plt.xlabel("Departure Hour")
plt.ylabel("Average Passengers per Trip")
plt.xticks(range(0, 24))
plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "11_hourly_passenger_demand.png",
    dpi=150
)

plt.close()


# ==================================================
# 10. CHART 2: DAY-OF-WEEK DEMAND
# ==================================================

plt.figure(figsize=(11, 6))

sns.barplot(
    data=daily_summary,
    x="day_name",
    y="average_passengers",
    order=day_order
)

plt.title("Average Passenger Demand by Day of Week")
plt.xlabel("Day of Week")
plt.ylabel("Average Passengers per Trip")
plt.xticks(rotation=25)
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "12_day_of_week_demand.png",
    dpi=150
)

plt.close()


# ==================================================
# 11. CHART 3: WEEKDAY VS WEEKEND
# ==================================================

plt.figure(figsize=(8, 6))

sns.barplot(
    data=weekend_summary,
    x="day_type",
    y="average_passengers",
    order=["Weekday", "Weekend"]
)

plt.title("Weekday vs Weekend Passenger Demand")
plt.xlabel("Day Type")
plt.ylabel("Average Passengers per Trip")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "13_weekday_weekend_demand.png",
    dpi=150
)

plt.close()


# ==================================================
# 12. CHART 4: EXAM-DAY DEMAND
# ==================================================

plt.figure(figsize=(8, 6))

sns.barplot(
    data=exam_summary,
    x="exam_category",
    y="average_passengers",
    order=["Normal Day", "Exam Day"]
)

plt.title("Exam Day vs Normal Day Passenger Demand")
plt.xlabel("Day Category")
plt.ylabel("Average Passengers per Trip")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "14_exam_day_demand.png",
    dpi=150
)

plt.close()


# ==================================================
# 13. CHART 5: EVENT-DAY DEMAND
# ==================================================

plt.figure(figsize=(8, 6))

sns.barplot(
    data=event_summary,
    x="event_category",
    y="average_passengers",
    order=["Normal Day", "Event Day"]
)

plt.title("Event Day vs Normal Day Passenger Demand")
plt.xlabel("Day Category")
plt.ylabel("Average Passengers per Trip")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "15_event_day_demand.png",
    dpi=150
)

plt.close()


# ==================================================
# 14. KEY FINDINGS
# ==================================================

busiest_hour = hourly_summary.loc[
    hourly_summary["average_passengers"].idxmax()
]

quietest_hour = hourly_summary.loc[
    hourly_summary["average_passengers"].idxmin()
]

busiest_day = daily_summary.loc[
    daily_summary["average_passengers"].idxmax()
]

quietest_day = daily_summary.loc[
    daily_summary["average_passengers"].idxmin()
]


def get_category_finding(summary, category_column, first, second):

    values = summary.set_index(category_column)[
        "average_passengers"
    ]

    if first not in values.index or second not in values.index:
        return "Insufficient data to compare both categories."

    difference = values[first] - values[second]

    if difference > 0:
        return f"{first} has higher average demand by {difference:.2f} passengers."

    if difference < 0:
        return f"{second} has higher average demand by {abs(difference):.2f} passengers."

    return "Both categories have equal average demand."


weekend_finding = get_category_finding(
    weekend_summary,
    "day_type",
    "Weekday",
    "Weekend"
)

exam_finding = get_category_finding(
    exam_summary,
    "exam_category",
    "Exam Day",
    "Normal Day"
)

event_finding = get_category_finding(
    event_summary,
    "event_category",
    "Event Day",
    "Normal Day"
)


# ==================================================
# 15. GENERATE REPORT
# ==================================================

report = f"""# CampusFlow - EDA 4: Time-Based Demand Analysis

**Dataset:** Synthetic campus transportation data

## 1. Hourly Demand

{hourly_summary.to_markdown(index=False)}

Busiest departure hour:
- Hour: {int(busiest_hour['hour'])}:00
- Average passengers: {busiest_hour['average_passengers']}

Lowest-demand departure hour:
- Hour: {int(quietest_hour['hour'])}:00
- Average passengers: {quietest_hour['average_passengers']}

## 2. Day-of-Week Demand

{daily_summary.to_markdown(index=False)}

Highest-demand day:
- {busiest_day['day_name']}
- Average passengers: {busiest_day['average_passengers']}

Lowest-demand day:
- {quietest_day['day_name']}
- Average passengers: {quietest_day['average_passengers']}

## 3. Weekday vs Weekend

{weekend_summary.to_markdown(index=False)}

{weekend_finding}

## 4. Exam-Day Analysis

{exam_summary.to_markdown(index=False)}

{exam_finding}

## 5. Event-Day Analysis

{event_summary.to_markdown(index=False)}

{event_finding}

## 6. Generated Charts

1. charts/11_hourly_passenger_demand.png
2. charts/12_day_of_week_demand.png
3. charts/13_weekday_weekend_demand.png
4. charts/14_exam_day_demand.png
5. charts/15_event_day_demand.png

## 7. Generated Summary Files

1. summaries/hourly_demand_summary.csv
2. summaries/day_of_week_demand_summary.csv
3. summaries/weekday_weekend_summary.csv
4. summaries/exam_day_demand_summary.csv
5. summaries/event_day_demand_summary.csv

## 8. Interpretation

This analysis compares passenger demand across departure hours,
days of the week, weekdays, weekends, exam days, and event days.

These are descriptive comparisons. They do not establish that
a particular day category causes higher or lower passenger demand.

All results are based on the synthetic CampusFlow dataset.
"""

(OUTPUT_DIR / "04_time_based_analysis_report.md").write_text(
    report,
    encoding="utf-8"
)


# ==================================================
# 16. DISPLAY RESULTS
# ==================================================

print("\n========== HOURLY DEMAND ==========\n")
print(hourly_summary.to_string(index=False))

print("\n========== DAY-OF-WEEK DEMAND ==========\n")
print(daily_summary.to_string(index=False))

print("\n========== WEEKDAY VS WEEKEND ==========\n")
print(weekend_summary.to_string(index=False))

print("\n========== EXAM-DAY DEMAND ==========\n")
print(exam_summary.to_string(index=False))

print("\n========== EVENT-DAY DEMAND ==========\n")
print(event_summary.to_string(index=False))

print("\n========== KEY FINDINGS ==========")

print(
    f"Busiest hour: {int(busiest_hour['hour'])}:00"
)

print(
    f"Lowest-demand hour: {int(quietest_hour['hour'])}:00"
)

print(
    "Highest-demand day:",
    busiest_day["day_name"]
)

print(
    "Lowest-demand day:",
    quietest_day["day_name"]
)

print("Weekday/weekend:", weekend_finding)
print("Exam days:", exam_finding)
print("Event days:", event_finding)

print("\nAll analysis files saved successfully.")
print(f"Output directory: {OUTPUT_DIR}")

print("\nPhase 1B - EDA 4 completed successfully!")
