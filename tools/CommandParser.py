#pylint: disable=C0303 E0401

from argparse import ArgumentParser
from tools.subparsers.ShowSubParser import ShowSubParser
from tools.subparsers.CheckSubParser import CheckSubParser

class CommandParser:
    '''Processing command line arguments'''

    @staticmethod
    def create_parser() -> ArgumentParser:
        '''Return the full parser'''
        parser = ArgumentParser(
            prog='marp',
            description='Universal handler of data written by MaidModule. Runs from the command line on any OS.',
            epilog='(c) Ggorets0dev 2022'
        )
        parser.add_argument('-v', '--version', action='store_true', help='Version of Marp')

        subparsers = parser.add_subparsers(dest='command', description='Commands available for use: ')
        subparsers = ShowSubParser.add_subparser(subparsers)
        subparsers = CheckSubParser.add_subparser(subparsers)

        return parser

