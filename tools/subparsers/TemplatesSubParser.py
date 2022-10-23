#pylint: disable=C0303 C0301 E0401

from argparse import _SubParsersAction, Namespace
from loguru import logger
from models.Reading import Reading
from models.Header import Header

class TemplatesSubParser:
    '''Displaying stitched patterns for headers and readings'''

    @staticmethod
    def add_subparser(subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        check_subparser = subparsers.add_parser('templates', description='Displaying stitched patterns for headers and readings')
        check_subparser.add_argument('-he', '--header', action='store_true', help='Header pattern')
        check_subparser.add_argument('-re', '--reading', action='store_true', help='Reading pattern')
        return subparsers

    @staticmethod
    def run_templates(namespace : Namespace) -> None:
        '''Run if Templates subparser was called'''
        logger.info("type[value] is used to denote a variable with special type, the '[]' characters and type before them are omitted")

        if not namespace.header and not namespace.reading:
            print(f"Header pattern: {Header.PATTERN}")
            print(f"Readings pattern: {Reading.PATTERN}")

        else:
            if namespace.header:
                print(f"Header pattern: {Header.PATTERN}")

            if namespace.reading:
                print(f"Readings pattern: {Reading.PATTERN}")
            