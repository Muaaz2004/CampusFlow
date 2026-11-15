
from pyspark.sql import SparkSession
from pyspark.sql.functions import col


# 1. Create Spark Session
spark = (
    SparkSession.builder
    .appName("CampusFlow-Kafka-Streaming")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("CampusFlow Spark Kafka Consumer Started")


# 2. Connect to Kafka and read streaming data
kafka_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "shuttle-events")
    .option("startingOffsets", "earliest")
    .load()
)


# 3. Select the required Kafka columns
events = kafka_stream.select(
    col("value").cast("string").alias("event_json"),
    col("topic"),
    col("partition"),
    col("offset"),
    col("timestamp")
)


# 4. Display incoming events in the console
query = (
    events.writeStream
    .format("console")
    .outputMode("append")
    .option("truncate", "false")
    .start()
)


# 5. Keep the streaming application running
query.awaitTermination()
