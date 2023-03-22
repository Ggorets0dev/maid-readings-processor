'''ReduceSubParser location'''

from argparse import _SubParsersAction, Namespace
from loguru import logger
from models.ReadableFile import ReadableFile
from tools.FileParser import FileParser

class ReduceSubParser:
    '''Reducing file (deleting clones)'''

    @staticmethod
    def add_subparser(subparsers: _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        reduce_subparser = subparsers.add_parser('reduce', description='Reducing incoming data or files against patterns')
        reduce_subparser.add_argument('-i', '--input', nargs=1, type=ReadableFile, required=True, help='Path to the file with readings')
        return subparsers

    @staticmethod
    def run_reduce(namespace: Namespace) -> None:
        '''Run if reduce subparser was called'''
        file_path = FileParser.reduce_readings(file_path=namespace.input[0].name)
    
        if file_path is not None:
            logger.success(f"File {namespace.input[0].name} successfully reduced, result available at: {file_path}")
        else:
            logger.error("It was not possible to perform the reduction because the operation was interrupted")