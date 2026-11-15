
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    StringIndexer,
    OneHotEncoder,
    VectorAssembler
)
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

# --------------------------------------------------
# 1. START SPARK
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("CampusFlow-Deployment-Pipeline")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("\n========== CAMPUSFLOW DEPLOYMENT PIPELINE ==========\n")

# --------------------------------------------------
# 2. LOAD RAW TRAINING AND TESTING DATA
# --------------------------------------------------

train_df = spark.read.parquet("reports/ml/train")
test_df = spark.read.parquet("reports/ml/test")

print("Training records:", train_df.count())
print("Testing records:", test_df.count())

# --------------------------------------------------
# 3. DEFINE FEATURES
# --------------------------------------------------

categorical_features = [
    "route_id",
    "season",
    "weather",
    "source_stop",
    "destination_stop"
]

numeric_features = [
    "hour",
    "day_of_week",
    "temperature_c",
    "rainfall_mm",
    "is_exam_day",
    "is_event_day",
    "distance_km"
]

# --------------------------------------------------
# 4. STRING INDEXING
# --------------------------------------------------

indexer = StringIndexer(
    inputCols=categorical_features,
    outputCols=[c + "_index" for c in categorical_features],
    handleInvalid="keep"
)

# --------------------------------------------------
# 5. ONE-HOT ENCODING
# --------------------------------------------------

encoder = OneHotEncoder(
    inputCols=[c + "_index" for c in categorical_features],
    outputCols=[c + "_encoded" for c in categorical_features],
    handleInvalid="keep"
)

# --------------------------------------------------
# 6. ASSEMBLE ALL FEATURES
# --------------------------------------------------

assembler = VectorAssembler(
    inputCols=(
        numeric_features
        + [c + "_encoded" for c in categorical_features]
    ),
    outputCol="features"
)

# --------------------------------------------------
# 7. LINEAR REGRESSION MODEL
# --------------------------------------------------

lr = LinearRegression(
    featuresCol="features",
    labelCol="passenger_count",
    predictionCol="prediction",
    maxIter=100,
    regParam=0.1,
    elasticNetParam=0.0
)

# --------------------------------------------------
# 8. COMBINE ALL STAGES
# --------------------------------------------------

pipeline = Pipeline(
    stages=[
        indexer,
        encoder,
        assembler,
        lr
    ]
)

# --------------------------------------------------
# 9. TRAIN COMPLETE PIPELINE
# --------------------------------------------------

print("\nTraining complete ML pipeline...")

pipeline_model = pipeline.fit(train_df)

print("Pipeline training completed!")

# --------------------------------------------------
# 10. EVALUATE ON UNTOUCHED TEST DATA
# --------------------------------------------------

predictions = pipeline_model.transform(test_df)

evaluator_rmse = RegressionEvaluator(
    labelCol="passenger_count",
    predictionCol="prediction",
    metricName="rmse"
)

evaluator_mae = RegressionEvaluator(
    labelCol="passenger_count",
    predictionCol="prediction",
    metricName="mae"
)

evaluator_r2 = RegressionEvaluator(
    labelCol="passenger_count",
    predictionCol="prediction",
    metricName="r2"
)

rmse = evaluator_rmse.evaluate(predictions)
mae = evaluator_mae.evaluate(predictions)
r2 = evaluator_r2.evaluate(predictions)

print("\n========== FINAL PIPELINE RESULTS ==========")
print(f"RMSE: {rmse:.4f}")
print(f"MAE : {mae:.4f}")
print(f"R2  : {r2:.4f}")

# --------------------------------------------------
# 11. SAVE COMPLETE PIPELINE
# --------------------------------------------------

pipeline_path = "reports/ml/campusflow_demand_pipeline"

pipeline_model.write().overwrite().save(pipeline_path)

print("\nPipeline saved successfully!")
print("Location:", pipeline_path)

# --------------------------------------------------
# 12. SAVE TEST PREDICTIONS
# --------------------------------------------------

prediction_path = "reports/ml/deployment_test_predictions"

(
    predictions
    .select(
        "travel_date",
        "passenger_count",
        "prediction"
    )
    .write
    .mode("overwrite")
    .parquet(prediction_path)
)

print("Test predictions saved:", prediction_path)

# --------------------------------------------------
# 13. DISPLAY SAMPLE PREDICTIONS
# --------------------------------------------------

print("\nSample predictions:")

predictions.select(
    "travel_date",
    "passenger_count",
    "prediction"
).show(15, truncate=False)

print("\nCampusFlow deployment pipeline completed!")

spark.stop()
