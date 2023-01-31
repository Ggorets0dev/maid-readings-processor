'''Main CommandParser location'''

from argparse import ArgumentParser
from tools.subparsers.ShowSubParser import ShowSubParser
from tools.subparsers.CheckSubParser import CheckSubParser
from tools.subparsers.ReduceSubParser import ReduceSubParser
from tools.subparsers.CalcSubParser import CalcSubParser
from tools.subparsers.TemplateSubParser import TemplateSubParser
from tools.subparsers.SplitSubParser import SplitSubParser
from tools.subparsers.AliasSubParser import AliasSubParser
from tools.subparsers.GraphSubParser import GraphSubParser

class CommandParser:
    '''Processing command line arguments'''

    @staticmethod
    def create_parser() -> ArgumentParser:
        '''Return the full parser'''
        parser = ArgumentParser(
            prog='marp',
            description='Universal handler of data written by MaidModule. Runs from the command line on any OS',
            epilog='Ggorets0dev (nikgorets4work@gmail.com)'
        )
        parser.add_argument('-v', '--version', action='store_true', help='Version of Marp')

        # SECTION - Connecting subparsers (commands) to the main parser
        subparsers = parser.add_subparsers(dest='command', description='Commands available for use: ')
        subparsers = ShowSubParser.add_subparser(subparsers)
        subparsers = CheckSubParser.add_subparser(subparsers)
        subparsers = ReduceSubParser.add_subparser(subparsers)
        subparsers = CalcSubParser.add_subparser(subparsers)
        subparsers = TemplateSubParser.add_subparser(subparsers)
        subparsers = SplitSubParser.add_subparser(subparsers)
        subparsers = AliasSubParser.add_subparser(subparsers)
        subparsers = GraphSubParser.add_subparser(subparsers)
        # !SECTION

        return parser
