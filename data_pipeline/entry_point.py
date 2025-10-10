import argparse
import logging
from importlib import import_module

from data_pipeline.core.constant import LOG_FORMAT
from data_pipeline.core.util.configuration_util import SubparserBuilder


logging.basicConfig(format=LOG_FORMAT, level=logging.INFO,
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the data pipeline ETL."""
    parser = argparse.ArgumentParser()

    # Build subparsers from submodules

    subparsers = parser.add_subparsers()

    # Load the modules to execute the Subparser decorator
    modules = [
        'data_pipeline.real_estate',
        'data_pipeline.core',
        'data_pipeline.validation',
        'data_pipeline.validation'
    ]
    for m in modules:
        import_module(m)

    for build_fcn in SubparserBuilder.decoratees():
        build_fcn(subparsers)

    # Parse CLI with the parser

    namespace, extra = parser.parse_known_args()
    logger.info(f"namespace: {namespace}")
    command_line_args = vars(namespace)
    logger.info(f"command_line_args : {command_line_args}")

    etl_task_name = command_line_args["command"]
    logger.info(f"ETL task name: {etl_task_name}")

    # import module
    mod = import_module(etl_task_name)
    # Get the function in that imported module
    # etl_process is the function in the imported module
    function_name_in_imported_module = getattr(mod, "etl_process")

    if not callable(function_name_in_imported_module):
        raise ValueError(
            f'Module {etl_task_name} does not have a function "etl_process"')

    # Execute function in the imported module
    keys = [k for k in command_line_args.keys() if k != 'command']
    if keys:
        function_name_in_imported_module(**command_line_args)
    else:
        function_name_in_imported_module()


if __name__ == '__main__':
    main()
