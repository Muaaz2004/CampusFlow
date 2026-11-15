
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    StringIndexer,
    OneHotEncoder,
    VectorAssembler
)

# --------------------------------------------------
# 1. CREATE SPARK SESSION
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("CampusFlow-Feature-Encoding")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("\n======================================")
print(" CAMPUSFLOW FEATURE ENCODING")
print("======================================")


# --------------------------------------------------
# 2. LOAD PREPARED TRAINING AND TESTING DATA
# --------------------------------------------------

train_df = spark.read.parquet("reports/ml/train")
test_df = spark.read.parquet("reports/ml/test")

print("\n1. DATASETS LOADED")

print("Training Records:", train_df.count())
print("Testing Records :", test_df.count())


# --------------------------------------------------
# 3. DEFINE CATEGORICAL AND NUMERICAL FEATURES
# --------------------------------------------------

categorical_features = [
    "route_id",
    "season",
    "weather",
    "source_stop",
    "destination_stop"
]

numerical_features = [
    "hour",
    "day_of_week",
    "temperature_c",
    "rainfall_mm",
    "is_exam_day",
    "is_event_day",
    "distance_km"
]

print("\n2. CATEGORICAL FEATURES")
print(categorical_features)

print("\n3. NUMERICAL FEATURES")
print(numerical_features)


# --------------------------------------------------
# 4. DEFINE TARGET VARIABLE
# --------------------------------------------------

train_df = train_df.withColumnRenamed(
    "passenger_count", "label"
)

test_df = test_df.withColumnRenamed(
    "passenger_count", "label"
)

print("\n4. TARGET VARIABLE: label")


# --------------------------------------------------
# 5. STRING INDEXER
# --------------------------------------------------

indexer = StringIndexer(
    inputCols=categorical_features,
    outputCols=[
        feature + "_index"
        for feature in categorical_features
    ],
    handleInvalid="keep"
)


# --------------------------------------------------
# 6. ONE HOT ENCODER
# --------------------------------------------------

encoder = OneHotEncoder(
    inputCols=[
        feature + "_index"
        for feature in categorical_features
    ],
    outputCols=[
        feature + "_encoded"
        for feature in categorical_features
    ],
    handleInvalid="keep"
)


# --------------------------------------------------
# 7. VECTOR ASSEMBLER
# --------------------------------------------------

assembler_inputs = numerical_features + [
    feature + "_encoded"
    for feature in categorical_features
]

assembler = VectorAssembler(
    inputCols=assembler_inputs,
    outputCol="features",
    handleInvalid="error"
)


# --------------------------------------------------
# 8. CREATE ML PIPELINE
# --------------------------------------------------

pipeline = Pipeline(
    stages=[
        indexer,
        encoder,
        assembler
    ]
)


# --------------------------------------------------
# 9. FIT PIPELINE USING TRAINING DATA ONLY
# --------------------------------------------------

print("\n5. FITTING FEATURE PIPELINE")

# Fit preprocessing only on the earlier training period
encoder_fit_df = train_df.filter(
    col("travel_date") < "2025-08-01"
)

pipeline_model = pipeline.fit(encoder_fit_df)

print("Feature pipeline fitted successfully!")


# --------------------------------------------------
# 10. TRANSFORM TRAINING AND TESTING DATA
# --------------------------------------------------

train_encoded = pipeline_model.transform(train_df)
test_encoded = pipeline_model.transform(test_df)

print("\n6. FEATURE TRANSFORMATION COMPLETED")


# --------------------------------------------------
# 11. SELECT FINAL MODEL COLUMNS
# --------------------------------------------------

train_final = train_encoded.select(
    "features",
    "label",
    "travel_date"
)

test_final = test_encoded.select(
    "features",
    "label",
    "travel_date"
)


# --------------------------------------------------
# 12. VERIFY FINAL DATA
# --------------------------------------------------

print("\n7. FINAL TRAINING DATA")

train_final.show(5, truncate=False)

print("\n8. FINAL TESTING DATA")

test_final.show(5, truncate=False)

print("\n9. FINAL SCHEMA")

train_final.printSchema()

print("\nTraining Records:", train_final.count())
print("Testing Records :", test_final.count())


# --------------------------------------------------
# 13. SAVE ENCODED DATASETS
# --------------------------------------------------

train_final.write.mode("overwrite").parquet(
    "reports/ml/encoded_train"
)

test_final.write.mode("overwrite").parquet(
    "reports/ml/encoded_test"
)

print("\n10. ENCODED DATASETS SAVED")

print("Training: reports/ml/encoded_train")
print("Testing : reports/ml/encoded_test")


print("\n======================================")
print(" FEATURE ENCODING COMPLETED")
print("======================================")

spark.stop()
