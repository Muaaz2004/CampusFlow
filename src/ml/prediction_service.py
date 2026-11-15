
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType
)
from pyspark.ml import PipelineModel


# --------------------------------------------------
# 1. LOAD THE TRAINED MODEL
# --------------------------------------------------

def load_model():

    spark = (
        SparkSession.builder
        .appName("CampusFlow-Prediction-Service")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    model_path = "reports/ml/campusflow_demand_pipeline"

    model = PipelineModel.load(model_path)

    print("CampusFlow ML model loaded successfully!")

    return spark, model


# --------------------------------------------------
# 2. DEFINE INPUT DATA STRUCTURE
# --------------------------------------------------

input_schema = StructType([
    StructField("travel_date", StringType(), False),
    StructField("hour", IntegerType(), False),
    StructField("day_of_week", IntegerType(), False),
    StructField("route_id", StringType(), False),
    StructField("season", StringType(), False),
    StructField("weather", StringType(), False),
    StructField("temperature_c", DoubleType(), False),
    StructField("rainfall_mm", DoubleType(), False),
    StructField("is_exam_day", IntegerType(), False),
    StructField("is_event_day", IntegerType(), False),
    StructField("source_stop", StringType(), False),
    StructField("destination_stop", StringType(), False),
    StructField("distance_km", DoubleType(), False)
])


# --------------------------------------------------
# 3. PREDICT PASSENGER DEMAND
# --------------------------------------------------

def predict_demand(spark, model, input_records):

    if not input_records:
        raise ValueError("At least one input record is required.")

    input_df = spark.createDataFrame(
        input_records,
        schema=input_schema
    )

    predictions = model.transform(input_df)

    result = predictions.select(
        "travel_date",
        "route_id",
        "source_stop",
        "destination_stop",
        "prediction"
    )

    return result


# --------------------------------------------------
# 4. TEST THE PREDICTION SERVICE
# --------------------------------------------------

if __name__ == "__main__":

    spark, model = load_model()

    sample_records = [
        {
            "travel_date": "2026-11-16",
            "hour": 9,
            "day_of_week": 0,
            "route_id": "R01",
            "season": "Winter",
            "weather": "Clear",
            "temperature_c": 18.5,
            "rainfall_mm": 0.0,
            "is_exam_day": 0,
            "is_event_day": 0,
            "source_stop": "ST01",
            "destination_stop": "ST04",
            "distance_km": 1.3
        },
        {
            "travel_date": "2026-11-16",
            "hour": 17,
            "day_of_week": 0,
            "route_id": "R03",
            "season": "Winter",
            "weather": "Cloudy",
            "temperature_c": 17.0,
            "rainfall_mm": 1.5,
            "is_exam_day": 1,
            "is_event_day": 0,
            "source_stop": "ST04",
            "destination_stop": "ST06",
            "distance_km": 1.8
        }
    ]

    result = predict_demand(
        spark,
        model,
        sample_records
    )

    print("\n========== PASSENGER DEMAND PREDICTIONS ==========")

    result.show(truncate=False)

    spark.stop()
