#pylint: disable=C0303 C0301 E0401 E0611

from argparse import _SubParsersAction, Namespace
from colorama import Fore, Style
from loguru import logger
from models.Reading import Reading
from models.Header import Header
from models.CountedReading import CountedReading
from tools.text_formatting_utils import cprint

class TemplatesSubParser:
    '''Displaying stitched patterns for headers and readings'''

    @staticmethod
    def add_subparser(subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        check_subparser = subparsers.add_parser('templates', description='Displaying stitched patterns for headers and readings')
        check_subparser.add_argument('-he', '--header', action='store_true', help='Header pattern')
        check_subparser.add_argument('-re', '--reading', action='store_true', help='Reading pattern')
        check_subparser.add_argument('-cr', '--calculated-reading', action='store_true', help='Calculated reading pattern')
        return subparsers

    @staticmethod
    def run_templates(namespace : Namespace) -> None:
        '''Run if Templates subparser was called'''
        logger.info("type[value] is used to denote a variable with special type")

        print("\nData type notation:\nint - integer\nfloat - fractional\ntime - time (hours, minutes, seconds, milliseconds)\ndatetime - date and time (year, month, day + time)\n")

        if not namespace.header and not namespace.reading and not namespace.calculated_reading:
            cprint(msg=f"Header pattern: {Header.PATTERN}", fore=Fore.WHITE, style=Style.BRIGHT)
            cprint(msg=f"Reading pattern: {Reading.PATTERN}", fore=Fore.WHITE, style=Style.BRIGHT)
            cprint(msg=f"Calculated reading pattern: {CountedReading.PATTERN}", fore=Fore.WHITE, style=Style.BRIGHT)

        if namespace.header:
            cprint(msg=f"Header pattern: {Header.PATTERN}", fore=Fore.WHITE, style=Style.BRIGHT)

        if namespace.reading:
            cprint(msg=f"Reading pattern: {Reading.PATTERN}", fore=Fore.WHITE, style=Style.BRIGHT)
        
        if namespace.calculated_reading:
            cprint(msg=f"Calculated reading pattern: {CountedReading.PATTERN}", fore=Fore.WHITE, style=Style.BRIGHT)
            