
# CampusFlow
## Intelligent Campus Shuttle Analytics, Real-Time Monitoring and Passenger Demand Prediction System

CampusFlow is a distributed data processing and analytics project developed using Apache Spark, Kafka, GraphX, PySpark MLlib and Streamlit.

The project simulates a university shuttle network and demonstrates historical data analysis, graph-based network analysis, real-time event processing and passenger demand prediction.

> **Important:** CampusFlow uses a reproducible synthetic dataset representing a fictional university campus. It does not contain actual LPU shuttle tracking or ridership data. All generated results and predictions are for academic demonstration.

---

## 1. Project Overview

The simulated campus transport network contains:

- 12 shuttle stops
- 4 shuttle routes
- 6 buses
- 30,000 historical trips
- 60,000 aggregate boarding and alighting events
- 365 days of synthetic weather data

### Main objectives

1. Generate and validate a reproducible transport dataset.
2. Perform distributed data processing using Apache Spark.
3. Analyze shuttle route connectivity using GraphX.
4. Process live shuttle events using Apache Kafka and Spark Structured Streaming.
5. Predict passenger demand using PySpark MLlib.
6. Visualize historical, network and live analytics through Streamlit.

---

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.13.2 | Application development |
| Java 21.0.12 | Spark runtime |
| Apache Spark 4.2.0 | Distributed processing |
| PySpark 4.2.0 | Python interface for Spark |
| Spark SQL | Structured data processing |
| RDD | Distributed collection processing |
| GraphX | Shuttle network analysis |
| Apache Kafka 3.9.1 | Event streaming |
| PySpark MLlib | Passenger demand prediction |
| Pandas and NumPy | Data processing |
| Streamlit 1.67.0 | Interactive dashboard |
| Plotly 7.1.0 | Interactive visualizations |
| Matplotlib and Seaborn | Exploratory data analysis |

---

## 3. System Architecture

```text
             Synthetic Historical Dataset
                         |
                         v
                 Data Generation
                         |
                         v
                Exploratory Analysis
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
          Spark       GraphX      MLlib
          SQL         Network     Prediction
             |        Analysis       |
             v                       |
          Parquet                    |
             |                       |
             +-----------+-----------+
                         |
                         v
                  Streamlit Dashboard
                         ^
                         |
Python Live Producer --> Kafka Topic
                         |
                         v
               Spark Structured Streaming
                         |
                         v
                 Event Validation
                  and Deduplication
                         |
                         v
                  Parquet Storage
                         |
                         v
                 Live Monitoring
```

---

## 4. Project Modules

### Phase 1: Dataset Generation and Validation

Generates reproducible synthetic campus transport data.

Main files:

- `src/generate_dataset.py`
- `src/validate_dataset.py`

Data includes stops, routes, route-stop mappings, weather, trips and boarding events.

### Phase 2: Spark Data Processing

Demonstrates:

- Spark RDD operations
- DataFrame transformations
- Spark SQL queries
- Parquet storage
- Partitioning and partition pruning

### Phase 3: GraphX Network Analysis

Builds a directed campus shuttle network.

Analysis includes:

- Graph vertices and edges
- In-degree and out-degree
- Connected components
- PageRank
- Stop connectivity

### Phase 4: Real-Time Streaming

Uses Kafka and Spark Structured Streaming to process shuttle events.

Features:

- Kafka producer and consumer
- JSON event parsing
- Route-wise analytics
- Watermark-based event deduplication
- Parquet persistence
- Live dashboard monitoring

The boarding event dataset contains two aggregate events per trip: boarding at the origin and alighting at the destination. It is not continuous GPS or stop-by-stop vehicle telemetry.

### Phase 5: Passenger Demand Prediction

Uses PySpark MLlib Linear Regression.

Features include:

- Data preparation
- Feature engineering
- Categorical encoding
- Model training
- Hyperparameter tuning
- Model evaluation
- Saved deployment pipeline
- Prediction service

The model is trained using synthetic historical records.

### Phase 6: Streamlit Dashboard

Dashboard pages:

1. Overview
2. Routes & Stops
3. Demand Analytics
4. Demand Prediction
5. Live Monitoring
6. Network Analysis

---

## 5. Prerequisites

This setup is documented for Windows and PowerShell.

Install or configure:

- Python 3.13.2
- Java JDK 21
- Apache Spark 4.2.0
- Apache Kafka 3.9.1
- Visual Studio Code (recommended)

The project uses the locally installed Spark distribution.

PySpark and Py4J are loaded from Spark's bundled Python libraries through `setup_spark.ps1`.

Do not assume that installing PySpark through pip alone reproduces this environment.

---

## 6. Installation and Environment Setup

### Step 1: Clone the repository

```powershell
git clone https://github.com/YOUR_USERNAME/CampusFlow.git
cd CampusFlow
```

### Step 2: Create a Python virtual environment

Python 3.13.2 is used for the verified development environment.

```powershell
py -3.13 -m venv .venv-spark313
.\.venv-spark313\Scripts\Activate.ps1
```

### Step 3: Install Python dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 4: Install Java and Apache Spark

Install:
- Java JDK 21
- Apache Spark 4.2.0

Configure the `JAVA_HOME` and `SPARK_HOME` paths in `setup_spark.ps1` according to your local installation directories.

### Step 5: Configure the Spark environment

```powershell
.\setup_spark.ps1
```

This script configures Java, Spark, PySpark and Py4J using the bundled Spark Python libraries.

Verify the PySpark installation:

```powershell
python -c "import pyspark; print(pyspark.__version__)"
```

Expected version:

```text
4.2.0
```

**Note:** PySpark and Py4J are supplied through the local Apache Spark distribution rather than installed through `requirements.txt`. Run `setup_spark.ps1` in every new PowerShell terminal before executing Spark-based modules.

## 7. Dataset Generation and Validation

CampusFlow includes a reproducible synthetic dataset under `data/raw/`.

To regenerate the default dataset:

```powershell
python -m src.generate_dataset --output-dir . --trips 30000 --days 365 --seed 20261105 --start-date 2025-01-01
```

To validate the generated dataset:

```powershell
python -m src.validate_dataset --project-root .
```

The validation script checks stop and route references, trip counts, weather coverage, passenger capacity, occupancy ranges, boarding events and synthetic data labeling.

A successful validation returns:

```text
"valid": true
```

**Note:** Regenerating the dataset overwrites the corresponding generated files in `data/raw/`. The dataset is entirely synthetic and does not represent actual university shuttle records.
## 8. Machine Learning Model Preparation

CampusFlow uses PySpark MLlib Linear Regression to predict passenger demand.

After cloning the repository and configuring the Spark environment, execute the following scripts from the project root in the specified order.

### Step 1: Inspect the historical dataset (optional)

```powershell
python -m src.ml.01_prepare_ml_data
```

This script loads the historical trip dataset, corrects timestamp columns, inspects the schema and analyzes the passenger count target variable.

### Step 2: Feature engineering and data splitting

```powershell
python -m src.ml.02_feature_engineering
```

Creates model features and performs chronological training and testing splits.

Outputs:
- `reports/ml/train`
- `reports/ml/test`

### Step 3: Encode features

```powershell
python -m src.ml.03_encode_features
```

Encodes categorical variables and assembles the feature vectors.

Outputs:
- `reports/ml/encoded_train`
- `reports/ml/encoded_test`

### Step 4: Train the initial Linear Regression model

```powershell
python -m src.ml.04_train_linear_regression
```

Trains the initial passenger demand prediction model.

### Step 5: Tune model hyperparameters

```powershell
python -m src.ml.05_tune_linear_regression
```

Evaluates different regularization settings using the validation dataset.

### Step 6: Evaluate the final model

```powershell
python -m src.ml.06_final_model_evaluation
```

Evaluates the final model using the chronological test dataset and generates performance metrics.

### Step 7: Save the deployment pipeline

```powershell
python -m src.ml.07_save_deployment_pipeline
```

Creates and saves the complete ML deployment pipeline, including feature transformations and Linear Regression.

The final model is saved at:

```text
reports/ml/campusflow_demand_pipeline/
```

### Step 8: Test the prediction service

```powershell
python -m src.ml.prediction_service
```

Loads the saved deployment pipeline and generates sample passenger demand predictions.

**Important:** The `reports/` directory is excluded from GitHub because it contains generated datasets, model artifacts and processing outputs. Run the ML pipeline before starting the Demand Prediction dashboard on a fresh installation.

## 9. Running the Dashboard

From the project root, activate the environment and configure Spark:

```powershell
.\.venv-spark313\Scripts\Activate.ps1
.\setup_spark.ps1
```

Start Streamlit:

```powershell
streamlit run app.py
```

Open the local URL displayed in the terminal.

---

## 10. Running the Kafka Streaming Pipeline

CampusFlow uses Apache Kafka and Spark Structured Streaming to process synthetic shuttle events and store them in Parquet format.

### Prerequisites

- Java JDK 21
- Apache Kafka 3.9.1
- Apache Spark 4.2.0
- Python environment configured using `setup_spark.ps1`

### Step 1: Start the Kafka server

Open PowerShell Terminal 1.

Configure Java:

```powershell
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-21.0.12.8-hotspot"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
```

Start Kafka using the KRaft configuration:

```powershell
C:\kafka\bin\windows\kafka-server-start.bat C:\kafka\config\kraft\server.properties
```

Keep this terminal running.

**Note:** Update the Java and Kafka paths according to your local installation.

### Step 2: Create the Kafka topic

Open PowerShell Terminal 2 and execute:

```powershell
C:\kafka\bin\windows\kafka-topics.bat --create --if-not-exists --topic shuttle-events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

This creates the `shuttle-events` topic if it does not already exist.

### Step 3: Start the Spark Parquet writer

In Terminal 2, activate the Python environment and configure Spark:

```powershell
.\.venv-spark313\Scripts\Activate.ps1
.\setup_spark.ps1
```

Start the streaming writer:

```powershell
python -m src.streaming.spark_parquet_writer
```

Keep this process running. It consumes Kafka messages, parses JSON events, applies watermark-based deduplication and writes events to Parquet storage.

### Step 4: Start the live event producer

Open PowerShell Terminal 3.

Activate the Python environment:

```powershell
.\.venv-spark313\Scripts\Activate.ps1
```

Run the producer:

```powershell
python -m src.streaming.kafka_live_producer
```

The producer publishes synthetic shuttle events with unique replay IDs to the Kafka topic.

### Step 5: Verify the stored events

After the producer finishes, open another PowerShell terminal, activate the Spark environment and run:

```powershell
.\.venv-spark313\Scripts\Activate.ps1
.\setup_spark.ps1
python -m src.streaming.verify_parquet
```

The verification script checks the total number of records, unique event IDs and duplicate records.

### Step 6: View live monitoring

Start the Streamlit dashboard in another configured terminal:

```powershell
streamlit run app.py
```

Open the displayed local URL and navigate to **Live Monitoring** to view the processed shuttle events and analytics.

**Important:** Start the Kafka server before the Spark writer and producer. Keep the Kafka server and Spark writer running while publishing events. The streaming output and checkpoint directories are generated locally and are not included in the GitHub repository.


## 11. Running the ML Prediction Service

Activate the Spark environment:

```powershell
.\.venv-spark313\Scripts\Activate.ps1
.\setup_spark.ps1
```

Run:

```powershell
python -m src.ml.prediction_service
```

The service loads the saved MLlib pipeline and generates passenger demand predictions.

---

## 12. Testing

The project includes validation and module-level tests.

Dataset validation:

```powershell
python src/validate_dataset.py --project-root .
```

Spark test modules are available under:

```text
src/spark_tests/
```

Streaming test modules are available under:

```text
src/streaming/
```

The Parquet verification module checks:

- Total records
- Unique event IDs
- Duplicate records

---

## 13. Important Data and Modeling Limitations

- All historical trips and live replay events are synthetic.
- The campus network and stop coordinates are illustrative.
- Boarding and alighting records are aggregate trip events.
- The ML model is trained on synthetic data and is not validated against actual campus ridership.
- PageRank measures network structure, not passenger demand.
- Watermark-based deduplication is bounded by its configured event-time watermark.
- Local development configuration is intended for academic demonstration, not production deployment.

---

## 14. Academic Project

**Project:** CampusFlow â€“ Intelligent Campus Shuttle Analytics, Real-Time Monitoring and Passenger Demand Prediction System

**Domain:** Cluster Computing, Big Data Analytics and Machine Learning

**Platform:** Local Windows development environment

**Dataset:** Reproducible synthetic campus transport dataset

