
from pyspark.sql import SparkSession

from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator


# --------------------------------------------------
# 1. CREATE SPARK SESSION
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("CampusFlow-Linear-Regression")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("\n======================================")
print(" CAMPUSFLOW LINEAR REGRESSION")
print("======================================")


# --------------------------------------------------
# 2. LOAD ENCODED DATASETS
# --------------------------------------------------

train_df = spark.read.parquet(
    "reports/ml/encoded_train"
)

test_df = spark.read.parquet(
    "reports/ml/encoded_test"
)

print("\n1. DATASETS LOADED")

print("Training Records:", train_df.count())
print("Testing Records :", test_df.count())


# --------------------------------------------------
# 3. INITIALIZE LINEAR REGRESSION
# --------------------------------------------------

lr = LinearRegression(
    featuresCol="features",
    labelCol="label",
    predictionCol="prediction",
    maxIter=100,
    regParam=0.0,
    elasticNetParam=0.0
)

print("\n2. LINEAR REGRESSION CONFIGURED")

print("Maximum Iterations: 100")
print("Regularization Parameter: 0.0")


# --------------------------------------------------
# 4. TRAIN THE MODEL
# --------------------------------------------------

print("\n3. TRAINING MODEL...")

lr_model = lr.fit(train_df)

print("MODEL TRAINING COMPLETED!")


# --------------------------------------------------
# 5. DISPLAY MODEL COEFFICIENTS
# --------------------------------------------------

print("\n4. MODEL PARAMETERS")

print("Intercept:", lr_model.intercept)

print("Number of Coefficients:",
      len(lr_model.coefficients))


# --------------------------------------------------
# 6. GENERATE TEST PREDICTIONS
# --------------------------------------------------

print("\n5. GENERATING TEST PREDICTIONS")

predictions = lr_model.transform(test_df)

predictions.select(
    "label",
    "prediction"
).show(15, truncate=False)


# --------------------------------------------------
# 7. EVALUATE MODEL PERFORMANCE
# --------------------------------------------------

print("\n6. MODEL EVALUATION")

evaluator = RegressionEvaluator(
    labelCol="label",
    predictionCol="prediction"
)

rmse = evaluator.evaluate(
    predictions,
    {evaluator.metricName: "rmse"}
)

mae = evaluator.evaluate(
    predictions,
    {evaluator.metricName: "mae"}
)

r2 = evaluator.evaluate(
    predictions,
    {evaluator.metricName: "r2"}
)

print("\n========== PERFORMANCE METRICS ==========")

print("RMSE:", rmse)
print("MAE :", mae)
print("R2  :", r2)


# --------------------------------------------------
# 8. SAVE TRAINED MODEL
# --------------------------------------------------

model_path = "reports/ml/linear_regression_model"

lr_model.write().overwrite().save(model_path)

print("\n7. MODEL SAVED SUCCESSFULLY")

print("Model Location:", model_path)


# --------------------------------------------------
# 9. SAVE TEST PREDICTIONS
# --------------------------------------------------

predictions_path = "reports/ml/test_predictions"

predictions.select(
    "travel_date",
    "label",
    "prediction"
).write.mode("overwrite").parquet(
    predictions_path
)

print("Predictions Location:", predictions_path)


print("\n======================================")
print(" LINEAR REGRESSION COMPLETED")
print("======================================")

spark.stop()
