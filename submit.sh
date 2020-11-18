export PYSPARK_PYTHON=python3
spark-submit \
    --master yarn \
    --deploy-mode cluster \
    --executor-memory 3G \
    $1