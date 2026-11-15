
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# --------------------------------------------------
# 1. CREATE SPARK SESSION
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("CampusFlow-Feature-Engineering")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("\n======================================")
print(" CAMPUSFLOW FEATURE ENGINEERING")
print("======================================")


# --------------------------------------------------
# 2. LOAD HISTORICAL DATA
# --------------------------------------------------

data_path = "data/raw/trips.csv"

trips_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(data_path)
)

# Correct time columns using travel_date
from pyspark.sql.functions import concat_ws, date_format, to_timestamp

trips_df = trips_df.withColumn(
    "departure_time",
    to_timestamp(
        concat_ws(
            " ",
            col("travel_date").cast("string"),
            date_format(col("departure_time"), "HH:mm:ss")
        ),
        "yyyy-MM-dd HH:mm:ss"
    )
)

trips_df = trips_df.withColumn(
    "arrival_time",
    to_timestamp(
        concat_ws(
            " ",
            col("travel_date").cast("string"),
            date_format(col("arrival_time"), "HH:mm:ss")
        ),
        "yyyy-MM-dd HH:mm:ss"
    )
)

print("\n1. HISTORICAL DATA LOADED")
print("Total Records:", trips_df.count())


# --------------------------------------------------
# 3. SELECT INPUT FEATURES AND TARGET
# --------------------------------------------------

selected_columns = [
    "hour",
    "day_of_week",
    "route_id",
    "season",
    "weather",
    "temperature_c",
    "rainfall_mm",
    "is_exam_day",
    "is_event_day",
    "source_stop",
    "destination_stop",
    "distance_km",
    "passenger_count",
    "travel_date"
]

ml_df = trips_df.select(*selected_columns)

print("\n2. SELECTED FEATURES")

print("Input Features:")
input_features = [
    column for column in selected_columns
    if column not in ["passenger_count", "travel_date"]
]

for feature in input_features:
    print("-", feature)

print("\nTarget Variable: passenger_count")


# --------------------------------------------------
# 4. CHECK MISSING VALUES
# --------------------------------------------------

print("\n3. MISSING VALUE ANALYSIS")

for column in ml_df.columns:
    missing_count = ml_df.filter(
        col(column).isNull()
    ).count()

    print(f"{column}: {missing_count}")


# --------------------------------------------------
# 5. CHRONOLOGICAL TRAIN-TEST SPLIT
# --------------------------------------------------

print("\n4. CHRONOLOGICAL DATA SPLIT")

split_date = "2025-10-20"

train_df = ml_df.filter(
    col("travel_date") < split_date
)

test_df = ml_df.filter(
    col("travel_date") >= split_date
)

print("Split Date:", split_date)

print("Training Records:", train_df.count())
print("Testing Records:", test_df.count())


# --------------------------------------------------
# 6. VERIFY DATE RANGES
# --------------------------------------------------

print("\n5. TRAINING DATE RANGE")

train_df.selectExpr(
    "MIN(travel_date) AS start_date",
    "MAX(travel_date) AS end_date"
).show()

print("\nTESTING DATE RANGE")

test_df.selectExpr(
    "MIN(travel_date) AS start_date",
    "MAX(travel_date) AS end_date"
).show()


# --------------------------------------------------
# 7. SAVE PREPARED DATASETS
# --------------------------------------------------

train_path = "reports/ml/train"
test_path = "reports/ml/test"

train_df.write.mode("overwrite").parquet(train_path)
test_df.write.mode("overwrite").parquet(test_path)

print("\n6. DATASETS SAVED SUCCESSFULLY")

print("Training Dataset:", train_path)
print("Testing Dataset:", test_path)


# --------------------------------------------------
# 8. DISPLAY SAMPLE DATA
# --------------------------------------------------

print("\n7. TRAINING DATA SAMPLE")

train_df.show(5, truncate=False)

print("\n======================================")
print(" FEATURE ENGINEERING COMPLETED")
print("======================================")

spark.stop()
