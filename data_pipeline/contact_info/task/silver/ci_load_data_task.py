from pyspark.sql import SparkSession
from data_pipeline.core.util import ci_bronze_loc, ci_silver_loc


# Initialize Spark session
spark = SparkSession.builder.getOrCreate()

def etl_process(**options):
    """
    Load table from Bronze to Silver zone
    """

    # Read bronze table
    ci_bronze = spark.read.table(ci_bronze_loc)
    print(f"Read data from {ci_bronze_loc}")

    # Write to silver table
    spark.sql(f"CREATE TABLE IF NOT EXISTS {ci_silver_loc} USING DELTA")
    ci_bronze.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(ci_silver_loc)

    print(f"Successfully load data into {ci_silver_loc}")