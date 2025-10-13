from pyspark.sql import functions as F

def etl_process(**options):
    # Fetch all the files in the folder
    based_path = "/Volumes/data_lake_dev/feature_raw_data/real_estate_parquet/"
    files = dbutils.fs.ls(based_path)
    print(files)

    # Get the latest file
    date = [ int(file.name.rstrip("/")) for file in files]
    latest_date = max(date)
    print(latest_date)

    # Read the latest file and add batch_id
    df = spark.read.parquet(based_path + str(latest_date))
    re_df = df.withColumn("batch_id", F.lit(latest_date))

    re_raw_loc = "data_lake_dev.feature_raw_data.re_raw"
    # Table existence check and append the table
    spark.sql(f"CREATE TABLE IF NOT EXISTS {re_raw_loc} USING DELTA")
    re_df.write.format("delta").mode("append").saveAsTable(re_raw_loc)

    # spark.sql(f"select * from {re_raw_loc}").display()