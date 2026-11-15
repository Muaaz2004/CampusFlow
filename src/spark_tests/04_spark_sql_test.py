
from pathlib import Path

from pyspark.sql import SparkSession

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "trips.csv"

spark = (
    SparkSession.builder
    .appName("CampusFlow Spark SQL")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

try:
    print("\n========== CAMPUSFLOW SPARK SQL ==========\n")

    # 1. Load dataset
    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(DATA_PATH))
    )

    # 2. Create temporary SQL view
    df.createOrReplaceTempView("campus_trips")

    print("Temporary SQL view created successfully!")

    # 3. Route-wise analysis
    print("\n========== ROUTE-WISE ANALYSIS ==========\n")

    route_result = spark.sql("""
        SELECT
            route_id,
            COUNT(*) AS total_trips,
            SUM(passenger_count) AS total_passengers,
            ROUND(AVG(passenger_count), 2) AS average_passengers
        FROM campus_trips
        GROUP BY route_id
        ORDER BY route_id
    """)

    route_result.show()

    # 4. Hour-wise passenger demand
    print("\n========== HOURLY PASSENGER DEMAND ==========\n")

    hourly_result = spark.sql("""
        SELECT
            hour,
            COUNT(*) AS total_trips,
            ROUND(AVG(passenger_count), 2) AS average_passengers,
            SUM(passenger_count) AS total_passengers
        FROM campus_trips
        GROUP BY hour
        ORDER BY hour
    """)

    hourly_result.show(20)

    # 5. Weekday vs weekend analysis
    print("\n========== WEEKDAY VS WEEKEND ==========\n")

    day_result = spark.sql("""
        SELECT
            CASE
                WHEN is_weekend = 1 THEN 'Weekend'
                ELSE 'Weekday'
            END AS day_type,
            COUNT(*) AS total_trips,
            ROUND(AVG(passenger_count), 2) AS average_passengers
        FROM campus_trips
        GROUP BY is_weekend
        ORDER BY is_weekend
    """)

    day_result.show()

    print("\nSUCCESS: Spark SQL analysis completed!")

finally:
    spark.stop()
