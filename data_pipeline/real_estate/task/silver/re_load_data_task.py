re_bronze_loc = "data_lake_dev.feature_bronze_data.re_transformed_bronze"
re_silver_loc = "data_lake_dev.feature_silver_data.real_estate"

def etl_process(**options):
    # Read bronze table
    re_bronze = spark.read.table(re_bronze_loc)

    # Write to silver table
    spark.sql(f"CREATE TABLE IF NOT EXISTS {re_silver_loc} USING DELTA")
    re_bronze.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(re_silver_loc)
    # re_bronze.display()