from argparse import _SubParsersAction, Namespace
from loguru import logger
from models.Reading import Reading
from models.Header import Header
from models.CountedReading import CountedReading
from tools.display_utils import ConstantValueOutput

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

        print("\nData type notation:\n" + 
            "   int - integer\n" + 
            "   float - fractional\n" + 
            "   time - time (hours, minutes, seconds, milliseconds)\n" + 
            "   datetime - date and time (year, month, day + time)\n")

        if not namespace.header and not namespace.reading and not namespace.calculated_reading:
            ConstantValueOutput('Header pattern', Header.PATTERN).display()
            ConstantValueOutput('Reading pattern', Reading.PATTERN).display()
            ConstantValueOutput('Calculated reading pattern', CountedReading.PATTERN).display()

        if namespace.header:
            ConstantValueOutput('Header pattern', Header.PATTERN).display()

        if namespace.reading:
            ConstantValueOutput('Reading pattern', Reading.PATTERN).display()
        
        if namespace.calculated_reading:
            ConstantValueOutput('Calculated reading pattern', CountedReading.PATTERN).display()
            