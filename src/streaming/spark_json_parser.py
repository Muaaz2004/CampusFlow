
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
    .appName("CampusFlow-JSON-Parser")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("CampusFlow JSON Parser Started")


# --------------------------------------------------
# 2. DEFINE JSON SCHEMA
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
# 3. CONNECT TO KAFKA
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
# 4. EXTRACT JSON STRING
# --------------------------------------------------

json_events = kafka_stream.select(
    col("value").cast("string").alias("event_json")
)


# --------------------------------------------------
# 5. PARSE JSON INTO STRUCTURED COLUMNS
# --------------------------------------------------

parsed_events = json_events.select(
    from_json(
        col("event_json"),
        event_schema
    ).alias("event")
).select("event.*")


# --------------------------------------------------
# 6. DISPLAY STRUCTURED STREAM
# --------------------------------------------------

query = (
    parsed_events.writeStream
    .format("console")
    .outputMode("append")
    .option("truncate", "false")
    .option("checkpointLocation", "checkpoints/json_parser")
    .start()
)

query.awaitTermination()
