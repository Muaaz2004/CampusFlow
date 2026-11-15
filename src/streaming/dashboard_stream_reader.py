
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    countDistinct,
    sum as spark_sum,
    when
)


def get_streaming_data():

    spark = (
        SparkSession.builder
        .appName("CampusFlow-Dashboard-Stream-Reader")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    path = "reports/streaming/parquet/events"

    try:

        # ----------------------------------------
        # 1. READ PERSISTED STREAMING EVENTS
        # ----------------------------------------

        events = spark.read.parquet(path)

        events = events.filter(
            col("event_id").isNotNull()
        )

        # ----------------------------------------
        # 2. ROUTE-WISE EVENT SUMMARY
        # ----------------------------------------

        summary = (
            events.groupBy(
                "route_id",
                "event_type"
            )
            .agg(
                count("event_id").alias("event_count"),
                spark_sum(
                    "passenger_delta"
                ).alias("passenger_total")
            )
        )

        summary_data = summary.toPandas()

        # ----------------------------------------
        # 3. RECENT EVENTS
        # ----------------------------------------

        events_data = (
            events.orderBy(
                col("kafka_timestamp").desc()
            )
            .limit(20)
            .toPandas()
        )

        # ----------------------------------------
        # 4. DASHBOARD METRICS
        # ----------------------------------------

        metrics_row = events.agg(
            count("*").alias("total_events"),

            countDistinct(
                "event_id"
            ).alias("unique_events"),

            countDistinct(
                "route_id"
            ).alias("active_routes"),

            spark_sum(
                when(
                    col("event_type") == "BOARD",
                    col("passenger_delta")
                ).otherwise(0)
            ).alias("boarding_passengers")
        ).first()

        metrics = {
            "total_events": metrics_row["total_events"] or 0,
            "unique_events": metrics_row["unique_events"] or 0,
            "active_routes": metrics_row["active_routes"] or 0,
            "boarding_passengers": metrics_row["boarding_passengers"] or 0
        }

        # ----------------------------------------
        # 5. RETURN ALL THREE RESULTS
        # ----------------------------------------

        return summary_data, events_data, metrics

    except Exception as e:

        print("Streaming data read error:", e)

        return None, None, None

    # Do not call spark.stop().
    # The SparkContext may be shared with the ML prediction service.
