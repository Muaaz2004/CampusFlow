# CampusFlow - EDA 5
## Feature Relationship and Correlation Analysis

### Dataset Information

- Total records analysed: 30000
- Target variable: passenger_count
- Numerical features analysed: 10
- Correlation method: Pearson correlation

### Correlation with Passenger Count

| feature          |   correlation_with_passenger_count |
|:-----------------|-----------------------------------:|
| available_seats  |                          0.247956  |
| is_event_day     |                          0.167471  |
| is_exam_day      |                          0.0735362 |
| distance_km      |                          0.0696209 |
| duration_minutes |                          0.0535807 |
| temperature_c    |                         -0.0290476 |
| hour             |                         -0.0746592 |
| rainfall_mm      |                         -0.120323  |
| day_of_week      |                         -0.407705  |
| is_weekend       |                         -0.512035  |

### Key Findings

- Strongest positive relationship: available_seats
  (correlation: 0.2480)

- Strongest negative relationship: is_weekend
  (correlation: -0.5120)

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
