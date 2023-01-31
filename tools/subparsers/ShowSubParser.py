'''ShowSubParser location'''

from argparse import _SubParsersAction, Namespace
from datetime import datetime
from loguru import logger
from tools.FileParser import FileParser
from tools.additional_datetime_utils import try_parse_datetime
from models.Config import Config
from models.ReadableFile import ReadableFile

class ShowSubParser:
    '''Output files or other data'''

    @classmethod
    def add_subparser(cls, subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        show_subparser = subparsers.add_parser('show', description='Displaying values on the screen without calculating any information')
        show_subparser.add_argument('-i', '--input', nargs=1, type=ReadableFile, required=True, help='Path to the file with readings')
        
        # NOTE - One of this targets must be specified
        show_subparser.add_argument('-he', '--header', action='store_true', help='Display the headers available by day (repetitions are ignored)')
        show_subparser.add_argument('-re', '--reading', action='store_true', help='Display all available raw readings')
        show_subparser.add_argument('-cr', '--calculated-reading', action='store_true', help='Display readings with already calculated speed and voltage')
        show_subparser.add_argument('-lc', '--line-count', action='store_true', help='Display number of lines in file')

        # NOTE - Modes of visualisation
        show_subparser.add_argument('-r', '--raw', action='store_true', help='Display values without visual processing')
        show_subparser.add_argument('-e', '--enumerate', action='store_true', help='Number displayed values')
        show_subparser.add_argument('-d', '--date-time', nargs='+', help='Readings or headers written in specified day and time (specify two for the range) (dd.mm.yyyy or dd.mm.yyyy-hh:mm:ss)')
        
        cls.SUBPARSER = show_subparser
        return subparsers

    @classmethod
    def run_show(cls, namespace : Namespace) -> None:
        '''Run if Show subparser was called'''
        resource_path = namespace.input[0].name
        config = Config.collect()

        # NOTE - Check the correctness of the passed arguments --date-time
        if (namespace.date_time and len(namespace.date_time) <= 2) or not namespace.date_time:
            datetime_start = try_parse_datetime(namespace.date_time[0]) if namespace.date_time and len(namespace.date_time) >= 1 else datetime(2000, 1, 1)
            datetime_end = try_parse_datetime(namespace.date_time[1], last_day=True) if namespace.date_time and len(namespace.date_time) == 2 else datetime(3000, 1, 1)
        else:
            logger.error("One or two dates can be passed with the --date-time argument")
            return


        # SECTION - Processing targets: --header --reading --calculated-reading --line-count
        if namespace.line_count:
            print(f"Lines in requested file: {FileParser.count_lines(file_path=resource_path)}")
        
        elif namespace.header:
            FileParser.show_headers(file_path=resource_path, datetime_start=datetime_start, datetime_end=datetime_end, raw=namespace.raw, to_enumerate=namespace.enumerate)

        elif namespace.reading or namespace.calculated_reading:
            FileParser.show_readings(file_path=resource_path, datetime_start=datetime_start, datetime_end=datetime_end, calculated=namespace.calculated_reading, raw=namespace.raw, to_enumerate=namespace.enumerate, config=config)

        else:
            logger.error("Display target not selected --header / --reading / --calculated-reading / --line-count)")
            cls.SUBPARSER.print_help()
        # !SECTION