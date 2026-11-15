
from pyspark.sql import SparkSession

# 1. Create Spark session
spark = (
    SparkSession.builder
    .appName("CampusFlow-Parquet-Verification")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("CampusFlow Parquet Verification Started")

# 2. Read Parquet files
parquet_df = spark.read.parquet(
    "reports/streaming/parquet/events"
)

# 3. Display schema
print("\nPARQUET DATA SCHEMA")
parquet_df.printSchema()

# 4. Count total records
total_records = parquet_df.count()

# 5. Count unique event IDs
unique_events = (
    parquet_df
    .select("event_id")
    .distinct()
    .count()
)

# 6. Calculate duplicate records
duplicate_records = total_records - unique_events

print("\nPARQUET VERIFICATION RESULTS")
print("--------------------------------")
print("Total Records       :", total_records)
print("Unique Event IDs    :", unique_events)
print("Duplicate Records   :", duplicate_records)
print("--------------------------------")

# 7. Display stored records
print("\nSTORED PARQUET DATA")

parquet_df.orderBy("event_id").show(
    30,
    truncate=False
)

spark.stop()
