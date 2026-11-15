
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    sum,
    count,
    when
)
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
    .appName("CampusFlow-Realtime-Analytics")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("CampusFlow Real-Time Analytics Started")


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
# 4. PARSE JSON MESSAGES
# --------------------------------------------------

parsed_events = kafka_stream.select(
    from_json(
        col("value").cast("string"),
        event_schema
    ).alias("event")
).select("event.*")


# --------------------------------------------------
# 5. FILTER VALID ANALYTICS EVENTS
# --------------------------------------------------

valid_events = parsed_events.filter(
    col("route_id").isNotNull() &
    col("event_type").isin("BOARD", "ALIGHT") &
    col("passenger_delta").isNotNull()
)


# --------------------------------------------------
# 6. REAL-TIME PASSENGER AGGREGATION
# --------------------------------------------------

route_analytics = (
    valid_events
    .groupBy("route_id")
    .agg(
        sum(
            when(
                col("event_type") == "BOARD",
                col("passenger_delta")
            ).otherwise(0)
        ).alias("boarding_passengers"),

        sum(
            when(
                col("event_type") == "ALIGHT",
                -col("passenger_delta")
            ).otherwise(0)
        ).alias("alighting_passengers"),

        sum(
            when(col("event_type") == "BOARD", 1).otherwise(0)
        ).alias("boarding_events"),

        sum(
            when(col("event_type") == "ALIGHT", 1).otherwise(0)
        ).alias("alighting_events"),

        count("*").alias("total_events")
    )
)


# --------------------------------------------------
# 7. DISPLAY REAL-TIME ANALYTICS
# --------------------------------------------------

query = (
    route_analytics.writeStream
    .format("console")
    .outputMode("complete")
    .option("truncate", "false")
    .option("numRows", "20")
    .option("checkpointLocation", "checkpoints/realtime_analytics")
    .start()
)

query.awaitTermination()
