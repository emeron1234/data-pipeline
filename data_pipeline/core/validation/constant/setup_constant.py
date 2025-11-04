import json
from pyspark.shell import spark
from pyspark.sql.types import StructType
from importlib import resources as pkg_resources
from data_pipeline.core.util.spark_util import load_dataframe_from_package

def config_file(job_type, test_type=None):
    if test_type is not None:
        return "qa_config_" + job_type + "_" + test_type + ".csv"
    else:
        return "qa_config_" + job_type + ".csv"
    

def load_config(qa_config, job_type=None):
    if job_type == 'cross_platform_count':
        schema = StructType.fromJson(
            json.loads(pkg_resources.read_text('we.pipeline.core.validation.schema', 'qa_cross_platform_config_schema.json')))
    else:
        schema = StructType.fromJson(
            json.loads(pkg_resources.read_text('we.pipeline.core.validation.schema', 'qa_config_schema.json')))

    df = load_dataframe_from_package(spark,
                                    'we.pipeline.core.validation.config',
                                    qa_config,
                                    'csv',
                                    schema,
                                    header=True, sep=',')
    return df