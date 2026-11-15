
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, lit, sum as spark_sum

from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator


# --------------------------------------------------
# 1. CREATE SPARK SESSION
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("CampusFlow-Final-Model-Evaluation")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("\n======================================")
print(" CAMPUSFLOW FINAL MODEL EVALUATION")
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
# 3. CONFIGURE SELECTED MODEL
# --------------------------------------------------

best_reg_param = 0.1

lr = LinearRegression(
    featuresCol="features",
    labelCol="label",
    predictionCol="prediction",
    maxIter=100,
    regParam=best_reg_param,
    elasticNetParam=0.0
)

print("\n2. SELECTED MODEL")
print("Algorithm: Ridge Linear Regression")
print("Regularization Parameter:", best_reg_param)


# --------------------------------------------------
# 4. TRAIN ON ALL TRAINING DATA
# --------------------------------------------------

print("\n3. TRAINING FINAL MODEL...")

final_model = lr.fit(train_df)

print("FINAL MODEL TRAINED SUCCESSFULLY!")


# --------------------------------------------------
# 5. GENERATE TEST PREDICTIONS
# --------------------------------------------------

print("\n4. GENERATING TEST PREDICTIONS")

predictions = final_model.transform(test_df)

predictions.select(
    "travel_date",
    "label",
    "prediction"
).show(15, truncate=False)


# --------------------------------------------------
# 6. EVALUATE MODEL
# --------------------------------------------------

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

print("\n5. FINAL MODEL PERFORMANCE")

print("RMSE:", rmse)
print("MAE :", mae)
print("R2  :", r2)


# --------------------------------------------------
# 7. CHECK NEGATIVE PREDICTIONS
# --------------------------------------------------

negative_predictions = predictions.filter(
    col("prediction") < 0
).count()

minimum_prediction = predictions.select(
    "prediction"
).agg(
    {"prediction": "min"}
).first()[0]

print("\n6. PREDICTION VALIDATION")

print("Negative Predictions:", negative_predictions)
print("Minimum Prediction  :", minimum_prediction)


# --------------------------------------------------
# 8. CREATE BASELINE FOR TEST COMPARISON
# --------------------------------------------------

training_average = train_df.select(
    avg("label").alias("average")
).first()["average"]

baseline_predictions = test_df.withColumn(
    "prediction",
    lit(training_average)
)

baseline_rmse = evaluator.evaluate(
    baseline_predictions,
    {evaluator.metricName: "rmse"}
)

baseline_mae = evaluator.evaluate(
    baseline_predictions,
    {evaluator.metricName: "mae"}
)

baseline_r2 = evaluator.evaluate(
    baseline_predictions,
    {evaluator.metricName: "r2"}
)

print("\n7. BASELINE COMPARISON")

print("Baseline RMSE:", baseline_rmse)
print("Model RMSE   :", rmse)

if rmse < baseline_rmse:
    print("Final model outperforms the baseline.")
else:
    print("Final model does not outperform the baseline.")


# --------------------------------------------------
# 9. SAVE FINAL MODEL
# --------------------------------------------------

model_path = "reports/ml/final_linear_regression_model"

final_model.write().overwrite().save(model_path)

print("\n8. FINAL MODEL SAVED")
print(model_path)


# --------------------------------------------------
# 10. SAVE FINAL PREDICTIONS
# --------------------------------------------------

prediction_path = "reports/ml/final_test_predictions"

predictions.select(
    "travel_date",
    "label",
    "prediction"
).write.mode("overwrite").parquet(
    prediction_path
)

print("\n9. FINAL PREDICTIONS SAVED")
print(prediction_path)


print("\n======================================")
print(" FINAL EVALUATION COMPLETED")
print("======================================")

spark.stop()
