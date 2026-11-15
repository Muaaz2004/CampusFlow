# CampusFlow data dictionary

**All records are synthetic.** The campus, stops, routes, ridership and coordinates are fictional/illustrative, not actual university operational data.

- `stops.csv`: `stop_id` (PK), `stop_name`, `zone`, `latitude`, `longitude`, `is_synthetic`.
- `routes.csv`: `route_id` (PK), `route_name`, `start_stop` and `end_stop` (FK to stops), `distance_km`, `is_synthetic`.
- `route_stops.csv`: `route_id` and `stop_id` (FKs), `stop_sequence` (1-based), `distance_from_previous_km`.
- `weather.csv`: one row per simulated date; `date`, `temperature_c`, `rainfall_mm`, `weather_condition`, `season`, `is_synthetic`.
- `trips.csv`: `trip_id` (PK), `bus_id`, `route_id`, `travel_date`, `departure_time`, `arrival_time`, `hour`, `day_of_week` (Monday=0), `day_name`, `is_weekend`, `season`, `weather`, `temperature_c`, `rainfall_mm`, `is_exam_day`, `is_event_day`, `available_seats`, `passenger_count`, `occupancy_rate`, `duration_minutes`, `source_stop`, `destination_stop`, `distance_km`.
- `boarding_events.jsonl`: one JSON object per line with `event_id`, `event_timestamp`, `trip_id`, `bus_id`, `route_id`, `stop_id`, `event_type`, `passenger_delta`, `occupancy_after`, `event_sequence`, `synthetic`. Each trip has a BOARD at origin and matching ALIGHT at destination.

## ML leakage prevention
Target: `passenger_count`. Candidate pre-trip features: route, hour, weekday/weekend, season, weather forecast, temperature/rainfall forecast, exam/event indicators, bus capacity and properly computed historical lag/rolling demand. Do not use the same trip's actual `passenger_count` or `occupancy_rate` as features. Use chronological train/test splitting.

## Simplifications
Each trip produces two aggregate events (all passengers board at origin and alight at destination). This is suitable for a Kafka/Structured Streaming demonstration, but is not stop-by-stop telemetry. Coordinates and route distances are illustrative.
