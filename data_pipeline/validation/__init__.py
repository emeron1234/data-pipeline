from argparse import ArgumentParser
from datetime import datetime
from re import match
from typing import Text

from data_pipeline.core.constant import environments, spaces
from data_pipeline.core.util.configuration_util import SubparserBuilder


@SubparserBuilder
def build_subparsers(subparsers) -> list[ArgumentParser]:
    """
    Build subparsers for the tasks in this module

    :param subparsers: A subparsers object from `argparse.ArgumentParser.add_subparsers()`
    :return: List of ArgumentParser
    """

    def year_month_day(s: Text) -> datetime:
        return datetime.fromisoformat(f'{s}T00:00:00+00:00')

    def parse_batch(s: Text) -> Text:
        if match(r'(load|[0-9]{8})', s):
            return s
        raise ValueError(f'Invalid batch format: {s}')

    parsers: list[ArgumentParser] = []
    parser: ArgumentParser

    object_types = ['re']
    job_types = ['rep']
    test_types = ['smoke', 'regression']
    zone = ['raw', 'bronze', 'silver']

    task = 'data_pipeline.validation.task.rep_val'
    parser = subparsers.add_parser(task)
    parser.set_defaults(command=task)
    parser.add_argument('-b', '--bucket', help='S3 bucket')
    parser.add_argument('-e', '--env', choices=environments, required=True, help='Environment')
    parser.add_argument('-p', '--space', choices=spaces, required=True, help='Space')
    parser.add_argument('-z', '--zone', choices=zone, required=False, help='Zone')
    parser.add_argument('-o', '--object_type', choices=object_types, required=True, help='Object_Types')
    parser.add_argument('-j', '--job_type', choices=job_types, required=True, help='Job_Types')
    parser.add_argument('-t', '--test_type', choices=test_types, required=False, help='Test_Types')
    parser.add_argument('--config', help='Configuration file')
    parsers.append(parser)

    return parsers
