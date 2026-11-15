
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, sum, count


# ==========================================
# 1. PROJECT PATH
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = PROJECT_ROOT / "data" / "raw" / "trips.csv"


# ==========================================
# 2. CREATE SPARK SESSION
# ==========================================

spark = (
    SparkSession.builder
    .appName("CampusFlow-Spark-Environment-Test")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


try:

    print("\n========== CAMPUSFLOW PYSPARK TEST ==========\n")

    print("Spark Version:", spark.version)
    print("Python Executable:", __import__("sys").executable)

    # ==========================================
    # 3. READ CAMPUSFLOW DATASET
    # ==========================================

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(DATA_FILE))
    )

    print("\nDataset loaded successfully!")

    print("Total Rows:", df.count())
    print("Total Columns:", len(df.columns))

    # ==========================================
    # 4. DISPLAY SCHEMA
    # ==========================================

    print("\n========== DATAFRAME SCHEMA ==========\n")

    df.printSchema()

    # ==========================================
    # 5. DISPLAY SAMPLE RECORDS
    # ==========================================

    print("\n========== SAMPLE RECORDS ==========\n")

    df.select(
        "trip_id",
        "route_id",
        "hour",
        "passenger_count",
        "occupancy_rate"
    ).show(5, truncate=False)

    # ==========================================
    # 6. DISTRIBUTED AGGREGATION
    # ==========================================

    print("\n========== ROUTE-WISE ANALYSIS ==========\n")

    route_summary = (
        df.groupBy("route_id")
        .agg(
            count("trip_id").alias("total_trips"),
            sum("passenger_count").alias("total_passengers"),
            avg("passenger_count").alias("average_passengers")
        )
        .orderBy("route_id")
    )

    route_summary.show(truncate=False)

    # ==========================================
    # 7. FINAL VERIFICATION
    # ==========================================

    total_trips = df.count()

    print("\n========== FINAL RESULT ==========")

    if total_trips == 30000:
        print("SUCCESS: All 30,000 trips processed!")
    else:
        print("WARNING: Unexpected trip count:", total_trips)

    print("\nCampusFlow PySpark test completed!")

finally:
    spark.stop()
