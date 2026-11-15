
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    count, sum, avg, round,
    col, concat_ws, date_format, to_timestamp
)

# Project directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "trips.csv"

# Create Spark Session
spark = (
    SparkSession.builder
    .appName("CampusFlow DataFrame Analysis")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

try:
    print("\n========== CAMPUSFLOW DATAFRAME TEST ==========\n")

    # 1. Load CSV
    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(DATA_PATH))
    )
    df = (
    df
    .withColumn(
        "departure_time",
        to_timestamp(
            concat_ws(
                " ",
                col("travel_date").cast("string"),
                date_format(col("departure_time"), "HH:mm:ss")
            )
        )
    )
    .withColumn(
        "arrival_time",
        to_timestamp(
            concat_ws(
                " ",
                col("travel_date").cast("string"),
                date_format(col("arrival_time"), "HH:mm:ss")
            )
        )
    )
)

    # 2. Display schema
    print("\nDATAFRAME SCHEMA")
    df.printSchema()

    # 3. Display first 10 records
    print("\nFIRST 10 RECORDS")
    df.show(10, truncate=False)

    # 4. Dataset dimensions
    print("\nDATASET INFORMATION")
    print("Total Rows:", df.count())
    print("Total Columns:", len(df.columns))

    # 5. Route-wise passenger analysis
    print("\nROUTE-WISE PASSENGER ANALYSIS")

    route_analysis = (
        df.groupBy("route_id")
        .agg(
            count("*").alias("total_trips"),
            sum("passenger_count").alias("total_passengers"),
            round(avg("passenger_count"), 2)
            .alias("average_passengers")
        )
        .orderBy("route_id")
    )

    route_analysis.show()

    print("\nSUCCESS: Spark DataFrame analysis completed!")

finally:
    spark.stop()
