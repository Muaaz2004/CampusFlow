
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
    .appName("CampusFlow-Event-Deduplication")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("CampusFlow Event Deduplication Started")


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
# 7. REMOVE DUPLICATE EVENTS
# --------------------------------------------------

deduplicated_events = (
    valid_events
    .withWatermark("kafka_timestamp", "2 hours")
    .dropDuplicates(["event_id"])
)


# --------------------------------------------------
# 8. DISPLAY DEDUPLICATED EVENTS
# --------------------------------------------------

query = (
    deduplicated_events.writeStream
    .format("console")
    .outputMode("append")
    .option("truncate", "false")
    .option("numRows", "30")
    .option("checkpointLocation", "checkpoints/deduplication")
    .start()
)

query.awaitTermination()
