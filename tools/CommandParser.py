#pylint: disable=C0303 E0401

from argparse import ArgumentParser
from tools.subparsers.ShowSubParser import ShowSubParser

class CommandParser:
    '''Processing command line arguments'''

    @staticmethod
    def create_parser() -> ArgumentParser:
        '''Return the full parser'''
        parser = ArgumentParser()
        subparsers = parser.add_subparsers(dest='command')

        subparsers = ShowSubParser.add_subparser(subparsers)

        return parser

