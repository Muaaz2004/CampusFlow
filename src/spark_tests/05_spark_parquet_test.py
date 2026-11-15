
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    count,
    sum,
    avg,
    round
)

# ==========================================
# PROJECT PATHS
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "trips.csv"

OUTPUT_DIR = PROJECT_ROOT / "reports" / "spark" / "parquet"

ROUTE_PATH = OUTPUT_DIR / "route_summary"
HOURLY_PATH = OUTPUT_DIR / "hourly_summary"


# ==========================================
# SPARK SESSION
# ==========================================

spark = (
    SparkSession.builder
    .appName("CampusFlow Parquet Storage")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")


try:
    print("\n========== CAMPUSFLOW PARQUET TEST ==========\n")

    # ==========================================
    # 1. LOAD DATASET
    # ==========================================

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(DATA_PATH))
    )

    print("Original dataset rows:", df.count())

    # ==========================================
    # 2. ROUTE-WISE AGGREGATION
    # ==========================================

    route_summary = (
        df.groupBy("route_id")
        .agg(
            count("*").alias("total_trips"),
            sum("passenger_count").alias("total_passengers"),
            round(avg("passenger_count"), 2)
            .alias("average_passengers")
        )
        .orderBy("route_id")
    )

    print("\nROUTE SUMMARY")
    route_summary.show()

    # ==========================================
    # 3. HOURLY AGGREGATION
    # ==========================================

    hourly_summary = (
        df.groupBy("hour")
        .agg(
            count("*").alias("total_trips"),
            sum("passenger_count").alias("total_passengers"),
            round(avg("passenger_count"), 2)
            .alias("average_passengers")
        )
        .orderBy("hour")
    )

    print("\nHOURLY SUMMARY")
    hourly_summary.show()

    # ==========================================
    # 4. SAVE AS PARQUET
    # ==========================================

    route_summary.write \
        .mode("overwrite") \
        .parquet(str(ROUTE_PATH))

    hourly_summary.write \
        .mode("overwrite") \
        .parquet(str(HOURLY_PATH))

    print("\nParquet files saved successfully!")

    # ==========================================
    # 5. READ PARQUET FILES AGAIN
    # ==========================================

    saved_routes = spark.read.parquet(str(ROUTE_PATH))

    saved_hourly = spark.read.parquet(str(HOURLY_PATH))

    print("\nREADING SAVED ROUTE PARQUET")

    saved_routes.orderBy("route_id").show()

    print("\nREADING SAVED HOURLY PARQUET")

    saved_hourly.orderBy("hour").show()

    # ==========================================
    # 6. VALIDATION
    # ==========================================

    route_count = saved_routes.count()
    hourly_count = saved_hourly.count()

    print("\n========== VALIDATION ==========")

    print("Route summary records:", route_count)
    print("Hourly summary records:", hourly_count)

    assert route_count == 4, "Expected 4 route records"
    assert hourly_count == 14, "Expected 14 hourly records"

    print("\nSUCCESS: Parquet storage and reading verified!")

finally:
    spark.stop()
