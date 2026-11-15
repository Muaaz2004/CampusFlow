
# ==========================================
# CAMPUSFLOW - SPARK ENVIRONMENT SETUP
# ==========================================

Write-Host "`nConfiguring CampusFlow Spark Environment..." -ForegroundColor Cyan

# Java configuration
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-21.0.12.8-hotspot"

# Spark configuration
$env:SPARK_HOME = "C:\Spark\spark-4.2.0-bin-hadoop3"

# Add Java and Spark to PATH
$env:Path = "$env:JAVA_HOME\bin;$env:SPARK_HOME\bin;$env:Path"

# Locate Spark's bundled Python libraries
$sparkPythonLib = Join-Path $env:SPARK_HOME "python\lib"

$py4jZip = Get-ChildItem $sparkPythonLib -Filter "py4j-*.zip" |
    Select-Object -First 1 -ExpandProperty FullName

$pysparkZip = Join-Path $sparkPythonLib "pyspark.zip"

# Check required files
if (-not (Test-Path $pysparkZip)) {
    throw "pyspark.zip not found!"
}

if (-not $py4jZip) {
    throw "Py4J ZIP file not found!"
}

# Configure Python
$env:PYTHONPATH = "$pysparkZip;$py4jZip"
$env:PYSPARK_PYTHON = (Get-Command python).Source

# Display configuration
Write-Host "`nCampusFlow Spark Environment Loaded!" -ForegroundColor Green

Write-Host "Python:"
python --version

Write-Host "`nJava:"
java -version

Write-Host "`nSpark Home: $env:SPARK_HOME"
Write-Host "PySpark Python: $env:PYSPARK_PYTHON"
Write-Host "PySpark Library: $pysparkZip"
Write-Host "Py4J Library: $py4jZip"

Write-Host "`nTesting PySpark import..." -ForegroundColor Cyan

python -c "import pyspark; print('PySpark Version:', pyspark.__version__)"

if ($LASTEXITCODE -ne 0) {
    throw "PySpark import failed. Check the Python environment."
}

Write-Host "`nSUCCESS: CampusFlow Spark is ready!" -ForegroundColor Green
