# CampusFlow - EDA 2: Route Analysis

**Dataset:** Synthetic campus transportation data

## 1. Route-wise analysis

| route_id   | route_name       |   total_trips |   total_passengers |   average_passengers |   average_occupancy |   average_duration |   average_distance |   buses_used |
|:-----------|:-----------------|--------------:|-------------------:|---------------------:|--------------------:|-------------------:|-------------------:|-------------:|
| R03        | Academic Express |          7487 |             156261 |                20.87 |                0.6  |              28.32 |                6.1 |            6 |
| R01        | North Loop       |          7560 |             145251 |                19.21 |                0.55 |              24.76 |                5.2 |            6 |
| R04        | Campus Circular  |          7447 |             128760 |                17.29 |                0.49 |              33.35 |                7.4 |            6 |
| R02        | South Connector  |          7506 |             110363 |                14.7  |                0.42 |              23.26 |                4.8 |            6 |

## 2. Route with the most trips

- Route: North Loop
- Total trips: 7560

## 3. Route with the highest total passenger demand

- Route: Academic Express
- Total passengers: 156261

## 4. Route with the highest average occupancy

- Route: Academic Express
- Average occupancy: 60.00%

## 5. Most frequently used stop

- Stop: North Hostel
- Total origin and destination trip references:
  15007.0

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
