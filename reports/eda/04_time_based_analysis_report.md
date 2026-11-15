# CampusFlow - EDA 4: Time-Based Demand Analysis

**Dataset:** Synthetic campus transportation data

## 1. Hourly Demand

|   hour |   total_trips |   total_passengers |   average_passengers |   average_occupancy |
|-------:|--------------:|-------------------:|---------------------:|--------------------:|
|      7 |           951 |               9147 |                 9.62 |                0.27 |
|      8 |          2455 |              53650 |                21.85 |                0.62 |
|      9 |          3681 |              92310 |                25.08 |                0.72 |
|     10 |          2173 |              34175 |                15.73 |                0.45 |
|     11 |          1645 |              20709 |                12.59 |                0.36 |
|     12 |          2230 |              36836 |                16.52 |                0.47 |
|     13 |          1879 |              28006 |                14.9  |                0.42 |
|     14 |          1587 |              19456 |                12.26 |                0.35 |
|     15 |          1863 |              26195 |                14.06 |                0.4  |
|     16 |          3086 |              54530 |                17.67 |                0.5  |
|     17 |          3776 |              88685 |                23.49 |                0.67 |
|     18 |          2827 |              58566 |                20.72 |                0.59 |
|     19 |          1271 |              14442 |                11.36 |                0.32 |
|     20 |           576 |               3928 |                 6.82 |                0.19 |

Busiest departure hour:
- Hour: 9:00
- Average passengers: 25.08

Lowest-demand departure hour:
- Hour: 20:00
- Average passengers: 6.82

## 2. Day-of-Week Demand

|   day_of_week | day_name   |   total_trips |   total_passengers |   average_passengers |   average_occupancy |
|--------------:|:-----------|--------------:|-------------------:|---------------------:|--------------------:|
|             0 | Monday     |          4133 |              86140 |                20.84 |                0.6  |
|             1 | Tuesday    |          4292 |              88478 |                20.61 |                0.59 |
|             2 | Wednesday  |          4512 |              93082 |                20.63 |                0.59 |
|             3 | Thursday   |          4239 |              87799 |                20.71 |                0.59 |
|             4 | Friday     |          4275 |              88312 |                20.66 |                0.59 |
|             5 | Saturday   |          4281 |              48521 |                11.33 |                0.32 |
|             6 | Sunday     |          4268 |              48303 |                11.32 |                0.32 |

Highest-demand day:
- Monday
- Average passengers: 20.84

Lowest-demand day:
- Sunday
- Average passengers: 11.32

## 3. Weekday vs Weekend

| day_type   |   total_trips |   total_passengers |   average_passengers |   average_occupancy |
|:-----------|--------------:|-------------------:|---------------------:|--------------------:|
| Weekday    |         21451 |             443811 |                20.69 |                0.59 |
| Weekend    |          8549 |              96824 |                11.33 |                0.32 |

Weekday has higher average demand by 9.36 passengers.

## 4. Exam-Day Analysis

| exam_category   |   total_trips |   total_passengers |   average_passengers |   average_occupancy |
|:----------------|--------------:|-------------------:|---------------------:|--------------------:|
| Exam Day        |          1209 |              25369 |                20.98 |                0.6  |
| Normal Day      |         28791 |             515266 |                17.9  |                0.51 |

Exam Day has higher average demand by 3.08 passengers.

## 5. Event-Day Analysis

| event_category   |   total_trips |   total_passengers |   average_passengers |   average_occupancy |
|:-----------------|--------------:|-------------------:|---------------------:|--------------------:|
| Event Day        |          2679 |              60106 |                22.44 |                0.64 |
| Normal Day       |         27321 |             480529 |                17.59 |                0.5  |

Event Day has higher average demand by 4.85 passengers.

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
