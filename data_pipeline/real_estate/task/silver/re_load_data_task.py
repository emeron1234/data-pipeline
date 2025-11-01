from pyspark.sql import SparkSession
from data_pipeline.core.util import re_bronze_loc, re_silver_loc


# Initialize Spark session
spark = SparkSession.builder.getOrCreate()

def etl_process(**options):
    """
    Load table from Bronze to Silver zone
    """

    # Read bronze table
    re_bronze = spark.read.table(re_bronze_loc)
    print(f"Read data from {re_bronze_loc}")

    # Write to silver table
    spark.sql(f"CREATE TABLE IF NOT EXISTS {re_silver_loc} USING DELTA")
    re_bronze.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(re_silver_loc)

    print(f"Successfully load data into {re_silver_loc}")