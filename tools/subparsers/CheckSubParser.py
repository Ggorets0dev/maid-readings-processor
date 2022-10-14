#pylint: disable=C0303  C0301 E0401

from argparse import _SubParsersAction, Namespace
from loguru import logger
from tools.FileParser import FileParser

class CheckSubParser:
    '''Checking files or other input data'''

    @staticmethod
    def add_subparser(subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        check_subparser = subparsers.add_parser('check', description='Checking incoming data or files against patterns')
        check_subparser.add_argument('-i', '--input', nargs=1, required=True, help='Path to the file with readings')
        check_subparser.add_argument('-p', '--pattern', action='store_true', help='Check that each line matches the header or reading pattern')
        check_subparser.add_argument('-t', '--time', action='store_true', help='Check whether each next date/time is later than the previous ones')
        return subparsers

    @staticmethod
    def run_check(namespace : Namespace) -> None:
        '''Run if Check subparser was called'''
        file_path = namespace.input[0]

        if namespace.pattern:
            FileParser.validate_readings_by_pattern(file_path)

        elif namespace.time:
            FileParser.validate_readings_by_time(file_path)
            
        else:
            logger.error("Check mode not selected (--pattern or --time)")
            