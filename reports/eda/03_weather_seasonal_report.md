# CampusFlow - EDA 3: Weather and Seasonal Analysis

**Dataset:** Synthetic campus transportation data

## 1. Seasonal Demand

| season   |   total_trips |   total_passengers |   average_passengers |   average_occupancy |   average_temperature |   average_rainfall |
|:---------|--------------:|-------------------:|---------------------:|--------------------:|----------------------:|-------------------:|
| autumn   |          5046 |              92800 |                18.39 |                0.52 |                 23.3  |               1.38 |
| monsoon  |          9969 |             172063 |                17.26 |                0.49 |                 26.94 |               6.72 |
| summer   |          7593 |             139342 |                18.35 |                0.53 |                 31.13 |               1.64 |
| winter   |          7392 |             136430 |                18.46 |                0.53 |                 13.11 |               1.52 |

Highest average seasonal demand:
- Season: winter
- Average passengers: 18.46

Lowest average seasonal demand:
- Season: monsoon
- Average passengers: 17.26

## 2. Weather Condition Analysis

| weather   |   total_trips |   total_passengers |   average_passengers |   average_occupancy |   average_temperature |   average_rainfall |
|:----------|--------------:|-------------------:|---------------------:|--------------------:|----------------------:|-------------------:|
| clear     |         18240 |             342165 |                18.76 |                0.54 |                 23.63 |               1.03 |
| cloudy    |          5532 |             100003 |                18.08 |                0.52 |                 23.85 |               0.88 |
| rainy     |          6228 |              98467 |                15.81 |                0.45 |                 25.12 |              11.87 |

Highest average demand by weather:
- Condition: clear
- Average passengers: 18.76

Lowest average demand by weather:
- Condition: rainy
- Average passengers: 15.81

## 3. Rainfall Analysis

| rainfall_category   |   total_trips |   average_passengers |   average_occupancy |   average_temperature |
|:--------------------|--------------:|---------------------:|--------------------:|----------------------:|
| No Rain             |           525 |                16.6  |                0.47 |                 23.42 |
| Light Rain          |         23934 |                18.54 |                0.53 |                 23.62 |
| Moderate Rain       |          3599 |                16.42 |                0.47 |                 25.16 |
| Heavy Rain          |          1942 |                15.02 |                0.43 |                 26.41 |

## 4. Correlation Analysis

- Temperature vs passenger count correlation: -0.0290
- Rainfall vs passenger count correlation: -0.1203

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

