
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    concat_ws,
    date_format,
    to_timestamp
)

# --------------------------------------------------
# 1. CREATE SPARK SESSION
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("CampusFlow-ML-Data-Preparation")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("\n======================================")
print(" CAMPUSFLOW ML DATA PREPARATION")
print("======================================")


# --------------------------------------------------
# 2. LOAD HISTORICAL TRIP DATASET
# --------------------------------------------------

data_path = "data/raw/trips.csv"

trips_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(data_path)
)

print("\n1. DATASET LOADED SUCCESSFULLY")


# --------------------------------------------------
# 3. CORRECT TIMESTAMP COLUMNS
# --------------------------------------------------

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


# --------------------------------------------------
# 4. VERIFY CORRECTED TIMESTAMPS
# --------------------------------------------------

print("\n========== TIMESTAMP VERIFICATION ==========")

trips_df.select(
    "travel_date",
    "departure_time",
    "arrival_time"
).show(5, truncate=False)

trips_df.selectExpr(
    "MIN(departure_time) AS earliest_departure",
    "MAX(departure_time) AS latest_departure"
).show(truncate=False)


# --------------------------------------------------
# 5. DISPLAY DATASET DIMENSIONS
# --------------------------------------------------

print("\n2. DATASET DIMENSIONS")

print("Total Rows    :", trips_df.count())
print("Total Columns :", len(trips_df.columns))


# --------------------------------------------------
# 6. DISPLAY COLUMN NAMES
# --------------------------------------------------

print("\n3. DATASET COLUMNS")

print(trips_df.columns)


# --------------------------------------------------
# 7. DISPLAY DATA TYPES
# --------------------------------------------------

print("\n4. DATASET SCHEMA")

trips_df.printSchema()


# --------------------------------------------------
# 8. DISPLAY SAMPLE RECORDS
# --------------------------------------------------

print("\n5. FIRST FIVE RECORDS")

trips_df.show(5, truncate=False)


# --------------------------------------------------
# 9. INSPECT TARGET VARIABLE
# --------------------------------------------------

print("\n6. TARGET VARIABLE ANALYSIS")

if "passenger_count" in trips_df.columns:

    print("Target Variable: passenger_count")

    trips_df.select(
        "passenger_count"
    ).describe().show()

    missing_target = trips_df.filter(
        col("passenger_count").isNull()
    ).count()

    print("Missing Target Values:", missing_target)

else:
    print("ERROR: passenger_count column not found!")


# --------------------------------------------------
# 10. INSPECT TRAVEL DATE
# --------------------------------------------------

print("\n7. TRAVEL DATE ANALYSIS")

trips_df.select(
    "travel_date"
).show(5, truncate=False)

trips_df.selectExpr(
    "MIN(travel_date) AS earliest_date",
    "MAX(travel_date) AS latest_date"
).show()


print("\n======================================")
print(" INITIAL DATA INSPECTION COMPLETED")
print("======================================")


spark.stop()
