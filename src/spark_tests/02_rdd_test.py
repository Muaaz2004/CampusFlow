
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("CampusFlow RDD Test")
    .master("local[*]")
    .getOrCreate()
)

sc = spark.sparkContext
sc.setLogLevel("ERROR")

try:
    print("\n========== CAMPUSFLOW RDD TEST ==========\n")

    # Create an RDD
    numbers = sc.parallelize([10, 20, 30, 40, 50])

    # Transformation: multiply each number by 2
    doubled = numbers.map(lambda x: x * 2)

    # Action: collect the results
    print("Original RDD:", numbers.collect())
    print("Doubled RDD:", doubled.collect())

    # Filter transformation
    filtered = numbers.filter(lambda x: x >= 30)
    print("Filtered RDD:", filtered.collect())

    # Reduce action
    total = numbers.reduce(lambda a, b: a + b)
    print("Sum:", total)

    # Count action
    print("Count:", numbers.count())

    print("\nSUCCESS: All RDD operations completed!")

finally:
    spark.stop()
