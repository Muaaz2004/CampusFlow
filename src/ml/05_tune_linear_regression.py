
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, avg

from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator


# --------------------------------------------------
# 1. CREATE SPARK SESSION
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("CampusFlow-Linear-Regression-Tuning")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("\n======================================")
print(" CAMPUSFLOW MODEL TUNING")
print("======================================")


# --------------------------------------------------
# 2. LOAD ENCODED TRAINING DATA
# --------------------------------------------------

data = spark.read.parquet(
    "reports/ml/encoded_train"
)

print("\n1. TRAINING DATA LOADED")
print("Total Records:", data.count())


# --------------------------------------------------
# 3. CREATE TRAINING AND VALIDATION SETS
# --------------------------------------------------

fit_df = data.filter(
    col("travel_date") < "2025-08-01"
)

validation_df = data.filter(
    col("travel_date") >= "2025-08-01"
)

print("\n2. TEMPORAL VALIDATION SPLIT")

print("Model Fitting Records:", fit_df.count())
print("Validation Records   :", validation_df.count())

fit_df.selectExpr(
    "MIN(travel_date) AS start_date",
    "MAX(travel_date) AS end_date"
).show()

validation_df.selectExpr(
    "MIN(travel_date) AS start_date",
    "MAX(travel_date) AS end_date"
).show()


# --------------------------------------------------
# 4. CREATE EVALUATION METRICS
# --------------------------------------------------

rmse_evaluator = RegressionEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="rmse"
)

mae_evaluator = RegressionEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="mae"
)

r2_evaluator = RegressionEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="r2"
)


# --------------------------------------------------
# 5. CREATE AVERAGE-PREDICTION BASELINE
# --------------------------------------------------

average_passengers = fit_df.select(
    avg("label").alias("average")
).first()["average"]

baseline_predictions = validation_df.withColumn(
    "prediction",
    lit(average_passengers)
)

baseline_rmse = rmse_evaluator.evaluate(
    baseline_predictions
)

baseline_mae = mae_evaluator.evaluate(
    baseline_predictions
)

baseline_r2 = r2_evaluator.evaluate(
    baseline_predictions
)

print("\n3. BASELINE PERFORMANCE")

print("Average Prediction:", average_passengers)
print("Baseline RMSE:", baseline_rmse)
print("Baseline MAE :", baseline_mae)
print("Baseline R2  :", baseline_r2)


# --------------------------------------------------
# 6. TEST REGULARIZATION VALUES
# --------------------------------------------------

regularization_values = [
    0.001,
    0.01,
    0.1,
    1.0,
    10.0
]

results = []

print("\n4. TESTING REGULARIZATION VALUES")

for value in regularization_values:

    print(f"\nTesting regParam = {value}")

    lr = LinearRegression(
        featuresCol="features",
        labelCol="label",
        predictionCol="prediction",
        maxIter=100,
        regParam=value,
        elasticNetParam=0.0
    )

    model = lr.fit(fit_df)

    predictions = model.transform(validation_df)

    rmse = rmse_evaluator.evaluate(predictions)
    mae = mae_evaluator.evaluate(predictions)
    r2 = r2_evaluator.evaluate(predictions)

    results.append({
        "regParam": value,
        "RMSE": rmse,
        "MAE": mae,
        "R2": r2,
        "model": model
    })

    print("RMSE:", rmse)
    print("MAE :", mae)
    print("R2  :", r2)


# --------------------------------------------------
# 7. SELECT BEST REGULARIZATION VALUE
# --------------------------------------------------

best_result = min(
    results,
    key=lambda result: result["RMSE"]
)

print("\n5. BEST MODEL CONFIGURATION")

print("Best regParam:", best_result["regParam"])
print("Best RMSE    :", best_result["RMSE"])
print("Best MAE     :", best_result["MAE"])
print("Best R2      :", best_result["R2"])


# --------------------------------------------------
# 8. COMPARE WITH BASELINE
# --------------------------------------------------

print("\n6. BASELINE VS BEST MODEL")

print("Baseline RMSE:", baseline_rmse)
print("Model RMSE   :", best_result["RMSE"])

if best_result["RMSE"] < baseline_rmse:
    print("Result: Model improved over the baseline.")
else:
    print("Result: Model did not beat the baseline.")


print("\n======================================")
print(" MODEL TUNING COMPLETED")
print("======================================")

spark.stop()
