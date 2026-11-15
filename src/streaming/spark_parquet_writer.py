
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    BooleanType,
    TimestampType
)

# --------------------------------------------------
# 1. CREATE SPARK SESSION
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("CampusFlow-Parquet-Streaming")
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0"
    )
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("CampusFlow Parquet Streaming Started")


# --------------------------------------------------
# 2. DEFINE EVENT SCHEMA
# --------------------------------------------------

event_schema = StructType([
    StructField("event_id", StringType(), True),
    StructField("event_timestamp", TimestampType(), True),
    StructField("trip_id", StringType(), True),
    StructField("bus_id", StringType(), True),
    StructField("route_id", StringType(), True),
    StructField("stop_id", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("passenger_delta", IntegerType(), True),
    StructField("occupancy_after", IntegerType(), True),
    StructField("event_sequence", IntegerType(), True),
    StructField("synthetic", BooleanType(), True)
])


# --------------------------------------------------
# 3. READ EVENTS FROM KAFKA
# --------------------------------------------------

kafka_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "shuttle-events")
    .option("startingOffsets", "earliest")
    .load()
)


# --------------------------------------------------
# 4. EXTRACT KAFKA TIMESTAMP AND JSON
# --------------------------------------------------

json_events = kafka_stream.select(
    col("timestamp").alias("kafka_timestamp"),
    col("value").cast("string").alias("event_json")
)


# --------------------------------------------------
# 5. PARSE JSON
# --------------------------------------------------

parsed_events = json_events.select(
    col("kafka_timestamp"),
    from_json(
        col("event_json"),
        event_schema
    ).alias("event")
).select(
    col("kafka_timestamp"),
    "event.*"
)


# --------------------------------------------------
# 6. FILTER VALID EVENTS
# --------------------------------------------------

valid_events = parsed_events.filter(
    col("event_id").isNotNull()
)


# --------------------------------------------------
# 7. DEDUPLICATE EVENTS
# --------------------------------------------------

deduplicated_events = (
    valid_events
    .withWatermark("kafka_timestamp", "2 hours")
    .dropDuplicates(["event_id"])
)


# --------------------------------------------------
# 8. WRITE STREAMING DATA TO PARQUET
# --------------------------------------------------

query = (
    deduplicated_events.writeStream
    .format("parquet")
    .outputMode("append")
    .option("path", "reports/streaming/parquet/events")
    .option(
        "checkpointLocation",
        "checkpoints/parquet_writer"
    )
    .start()
)

print("Writing deduplicated events to Parquet...")

query.awaitTermination()
