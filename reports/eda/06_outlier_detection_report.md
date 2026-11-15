# CampusFlow - EDA 6
## Outlier Detection and Data Quality Analysis

### Dataset Information

- Total records: 30000
- Duplicate records: 0
- Features analysed: 6
- Detection method: Interquartile Range (IQR)

### Data Quality Summary

| column           |   missing_values |   minimum |   maximum |
|:-----------------|-----------------:|----------:|----------:|
| passenger_count  |                0 |       0   |      40   |
| distance_km      |                0 |       4.8 |       7.4 |
| duration_minutes |                0 |      16   |      42   |
| temperature_c    |                0 |       8.1 |      35.9 |
| rainfall_mm      |                0 |       0   |      24.8 |
| available_seats  |                0 |      30   |      40   |

### Outlier Summary

| feature          |   Q1 |   Q3 |   IQR |   lower_bound |   upper_bound |   outlier_count |   outlier_percentage |
|:-----------------|-----:|-----:|------:|--------------:|--------------:|----------------:|---------------------:|
| passenger_count  | 12   | 24   |  12   |         -6    |         42    |               0 |             0        |
| distance_km      |  4.8 |  6.1 |   1.3 |          2.85 |          8.05 |               0 |             0        |
| duration_minutes | 24   | 31   |   7   |         13.5  |         41.5  |              55 |             0.183333 |
| temperature_c    | 18.3 | 29.4 |  11.1 |          1.65 |         46.05 |               0 |             0        |
| rainfall_mm      |  0.6 |  1.9 |   1.3 |         -1.35 |          3.85 |            5907 |            19.69     |
| available_seats  | 30   | 40   |  10   |         15    |         55    |               0 |             0        |

### Important Interpretation

The IQR method flags observations outside:

- Lower bound = Q1 - 1.5 * IQR
- Upper bound = Q3 + 1.5 * IQR

A flagged observation is not automatically an error.

For example, high rainfall or high passenger demand
may be valid observations.

Outliers must be investigated before deciding whether
to retain, transform, or remove them.

### Important Project Note

CampusFlow uses synthetic data.

The results describe the generated simulation and
should not be interpreted as actual campus transport data.
