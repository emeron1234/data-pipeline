from importlib import resources as pkg_resources
from pyspark.sql import DataFrame, SparkSession
from typing import Text, Union
from pyspark.sql.types import StructType


def load_dataframe_from_package(spark: SparkSession,
                                package: Text,
                                filename: Text,
                                fmt: Text,
                                schema: Union[StructType, Text],
                                **options) -> DataFrame:
    """
    Load a DataFrame from a resource in a package

    :param spark: A SparkSession instance
    :param package: Package name, e.g. 'we.pipeline.core.mapping'
    :param filename: A file to load
    :param fmt: File format
    :param schema: Schema of the file
    :param options: kwargs
    :return: A DataFrame
    """

    if filename is None or package is None:
        raise ValueError('package or filename is blank')

    contents = pkg_resources.read_text(package, filename)
    lines = contents.splitlines()

    rdd = spark.sparkContext.parallelize(lines)

    # DataFrameReader.csv() and .json() accept RDD
    # but .load() doesn't. Therefore, this function only
    # supports csv and json

    reader = spark.read \
        .schema(schema) \
        .options(**options)

    if fmt.lower() == 'csv':
        # noinspection PyTypeChecker
        df = reader.csv(rdd)
    elif fmt.lower() == 'json':
        # noinspection PyTypeChecker
        df = reader.json(rdd)
    else:
        raise ValueError('fmt must be either csv or json')

    return df