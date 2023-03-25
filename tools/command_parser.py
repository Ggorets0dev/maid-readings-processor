'''Main CommandParser location'''

from argparse import ArgumentParser
from tools.subparsers.show_subparser import ShowSubParser
from tools.subparsers.check_subparser import CheckSubParser
from tools.subparsers.reduce_subparser import ReduceSubParser
from tools.subparsers.calc_subparser import CalcSubParser
from tools.subparsers.template_subparser import TemplateSubParser
from tools.subparsers.split_subparser import SplitSubParser
from tools.subparsers.alias_subparser import AliasSubParser
from tools.subparsers.graph_subparser import GraphSubParser

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
