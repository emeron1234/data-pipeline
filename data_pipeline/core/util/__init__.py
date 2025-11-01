from pyspark.sql import SparkSession

re_bronze_loc = "data_lake_dev.feature_bronze_data.re_transformed_bronze"
re_silver_loc = "data_lake_dev.feature_silver_data.real_estate"

def get_dbutils(spark: SparkSession):
    """Safely retrieves dbutils whether running locally or on a databricks cluster

    :param spark: SparkSession.
    :return: A DBUtils object if code is executed on a Databricks cluster.
        None otherwise.
    """
    try:
        # pylint: disable=import-outside-toplevel
        from pyspark.dbutils import DBUtils  # noqa

        if "dbutils" not in locals():
            utils = DBUtils(spark)
            return utils

        return locals().get("dbutils")
    except ImportError:
        return None