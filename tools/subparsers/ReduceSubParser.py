#pylint: disable=C0303  C0301 E0401

from argparse import _SubParsersAction, Namespace
from loguru import logger
from tools.FileParser import FileParser

class ReduceSubParser:
    '''Reducing file (deleting clones)'''

    @staticmethod
    def add_subparser(subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        reduce_subparser = subparsers.add_parser('reduce', description='Reducing incoming data or files against patterns')
        reduce_subparser.add_argument('-i', '--input', nargs=1, required=True, help='Path to the file with readings')
        reduce_subparser.add_argument('-u', '--unchecked', action='store_true', help='Whether to check each line against the pattern (enabled by default)')
        return subparsers

    @staticmethod
    def run_reduce(namespace : Namespace) -> None:
        '''Run if reduce subparser was called'''
        file_path = FileParser.reduce_readings(file_path=namespace.input[0], check=not(namespace.unchecked))
    
        if file_path is not None:
            logger.success(f"File {namespace.input[0]} successfully reduced, result: {file_path}")
        else:
            logger.error("It was not possible to perform the reduction because the operation was interrupted")