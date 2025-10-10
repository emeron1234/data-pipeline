import os
import pathlib
import subprocess
import sys

import setuptools


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


GH_TOKEN = os.getenv('GH_TOKEN')

if GH_TOKEN is None:
    required = 'python-dotenv==1.0.0'
    # installed = {pkg.key for pkg in pkg_resources.working_set}
    # if required not in installed:
    install(required)
    from dotenv import load_dotenv

    # Load .env file
    load_dotenv()
    GH_TOKEN = os.getenv('GH_USERNAME') + ':' + os.getenv('GH_TOKEN')

PACKAGE_REQUIREMENTS = [
    'nameparser==1.1.2',
    # PySpark is provided by Databricks runtime - don't include in wheel
    # 'pyspark==3.3.0',
    'smartystreets_python_sdk==4.16.1',
    'PyYAML==6.0',
    'python-dotenv==1.0.0',
    "boto3==1.34.51",
    "pysftp==0.2.9",
    "pgpy==0.6.0",
    "jellyfish==1.1.0",
    # GraphFrames depends on PySpark - also excluded for serverless
    # "graphframes==0.6",
    "pymsteams==0.2.3",
    "paramiko==2.12.0"
]

DEV_REQUIREMENTS = [
    'nameparser==1.1.2',
    'pyspark==3.3.0',
    'smartystreets_python_sdk==4.16.1',
    # 'dbx>=0.7,<0.8',
    # Make sure use the latest version of the dbx
    'dbx>=0.8.19',
    'click==8.2.1',
    'typer==0.7.0',
    'requests>=2.28.0,<3.0.0',
    'python-dotenv==1.0.0',
    # below libraries are added from the altrata setup.py to run the pytest (unit test)
    "wheel",
    "pyyaml==6.0",
    "pytest==7.1.3",
    "pytest-cov==3.0.0",
    "mlflow",  #mlflow==1.29.0
    "delta-spark==2.1.0",
    "pandas==1.5.0",
    "freezegun==1.2.2",
    "black==22.8.0",
    "pylint==2.15.3",
    "numpy==1.23.1",
    "chispa==0.9.2",
    "urllib3<2",
    "typing_extensions==4.5.0",
    "psycopg2-binary==2.9.9",
    "elasticsearch==7.9.0",
    "certifi",
    "boto3==1.34.51",
    "pysftp==0.2.9",
    "pymsteams==0.2.3",
    "pgpy==0.6.0",
    "graphframes==0.6",
    "jellyfish==1.1.0",
    "soda-core==3.1.0",
    "soda-core-spark_df==3.1.0",
    "paramiko==2.12.0"
]

current_dir = pathlib.Path(__file__).parent.resolve()
long_description = (current_dir / 'README.md').read_text(encoding='utf-8')

setuptools.setup(
    name="data_pipeline",
    version="1.0.1",
    author="DataVerse & DataAvengers Team",
    author_email="haziq.matlan@gmail.com",
    description="This package contains all the necessary classes and functions for data engineering framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["**/test/**", "test_*"]),
    entry_points={
        'console_scripts': [
            'data-pipeline-etl = data_pipeline.entry_point:main' # Set as entry point for ETL - need to be insiden `data_pipeline` package
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    setup_requires=['setuptools', 'wheel'],
    install_requires=PACKAGE_REQUIREMENTS,
    extras_require={'dev': DEV_REQUIREMENTS},
    include_package_data=True,
    package_data={
        'data_pipeline.core.validation.config': ['*.csv', '*.json'],
        'data_pipeline.core.validation.yml_query': ["**/*.yml", "**/*.yaml"]
    }
)