
from pathlib import Path
from pyspark.sql import SparkSession

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "trips.csv"

OUTPUT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "spark"
    / "parquet"
    / "trips_by_route"
)

spark = (
    SparkSession.builder
    .appName("CampusFlow Parquet Partitioning")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

try:
    print("\n========== PARQUET PARTITIONING ==========\n")

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(DATA_PATH))
    )

    # Write data partitioned by route_id
    df.write \
        .mode("overwrite") \
        .partitionBy("route_id") \
        .parquet(str(OUTPUT_PATH))

    print("Partitioned Parquet data saved!")

    # Read partitioned data
    partitioned_df = spark.read.parquet(str(OUTPUT_PATH))

    print("\nTotal records:", partitioned_df.count())

    print("\nRoute-wise record counts:")

    partitioned_df.groupBy("route_id") \
        .count() \
        .orderBy("route_id") \
        .show()

    # Filter one route
    print("\nR03 records:")

    r03 = partitioned_df.filter("route_id = 'R03'")

    r03.select(
        "trip_id",
        "route_id",
        "passenger_count"
    ).show(5)

    # Explain query plan
    print("\nQUERY EXECUTION PLAN:")

    r03.explain("formatted")

    print("\nSUCCESS: Partitioning test completed!")

finally:
    spark.stop()

