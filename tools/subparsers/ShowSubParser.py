#pylint: disable=C0301 C0303 E0401 E0611

from argparse import _SubParsersAction, Namespace
from datetime import datetime
from loguru import logger
from tools.FileParser import FileParser
from tools.Calculator import Calculator
from tools.additional_datetime_utils import try_parse_datetime, is_datetime_in_interval
from models.Reading import Reading
from models.ReadableFile import ReadableFile
from models.CountedReading import CountedReading

class ShowSubParser:
    '''Output files or other data'''

    @staticmethod
    def add_subparser(subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        show_subparser = subparsers.add_parser('show', description='Displaying values on the screen without calculating any information')
        show_subparser.add_argument('-i', '--input', nargs=1, type=ReadableFile, required=True, help='Path to the file with readings')
        
        # NOTE - One of this targets must be specified
        show_subparser.add_argument('-he', '--header', action='store_true', help='Display the headers available by day (repetitions are ignored)')
        show_subparser.add_argument('-re', '--reading', action='store_true', help='Display all available readings (use -c for processed readings)')
        show_subparser.add_argument('-lc', '--line-count', action='store_true', help='Display number of lines in file')

        # NOTE - Modes of visualisation
        show_subparser.add_argument('-r', '--raw', action='store_true', help='Display values without visual processing')
        show_subparser.add_argument('-e', '--enumerate', action='store_true', help='Number displayed values')
        show_subparser.add_argument('-c', '--calculate', nargs=1, type=int, help='Verify the number of pulses in km/h and the analog value in volts with CALCULATE decimal places (disabled by default)')
        show_subparser.add_argument('-d', '--date-time', nargs='+', help='Readings or headers written in specified day and time (specify two for the range) (dd.mm.yyyy or dd.mm.yyyy-hh:mm:ss)')
        return subparsers

    @staticmethod
    def run_show(namespace : Namespace) -> None:
        '''Run if Show subparser was called'''

        resource_path = namespace.input[0].name

        # NOTE - Processing targets: --line-count
        if namespace.line_count:
            print(f"Lines in requested file: {FileParser.count_lines(file_path=resource_path)}")
            return

        # NOTE - Check if count of --date args is wrong
        if namespace.date_time and len(namespace.date_time) > 2:
            logger.error("One or two dates can be passed with the --date argument")
            return

        # NOTE - Filling parameters with values or None if no arguments are used
        datetime_start = try_parse_datetime(namespace.date_time[0]) if namespace.date_time and len(namespace.date_time) >= 1 else datetime(2000, 1, 1)
        datetime_end = try_parse_datetime(namespace.date_time[1]) if namespace.date_time and len(namespace.date_time) == 2 else datetime(3000, 1, 1)

        headers_readings = FileParser.parse_readings(file_path=resource_path)

        # NOTE - Use convertion of Reading to CountedReading with specified accuracy
        if namespace.calculate and namespace.reading:
            if namespace.calculate[0] > 0 and namespace.calculate[0] <= 5:
                headers_readings = Calculator.convert_readings(headers_readings)
            else:
                logger.error("Accuracy at --calculate must have a value between 1 and 5")
                return

        # SECTION - Processing targets: --header --reading --date
        found_any = False
        if namespace.header:
            last_header = None
            for header in headers_readings:
                if last_header and last_header.datetime.date() == header.datetime.date():
                    last_header = header
                    continue
                else:
                    last_header = header
                
                if is_datetime_in_interval(header.datetime, datetime_start, datetime_end):
                    header.display(raw=namespace.raw, to_enumerate=namespace.enumerate, time=False)
                    found_any = True
            
            if not found_any:
                logger.info('No headers was found on specified --datetime')
                return

        elif namespace.reading:
            for header in headers_readings:
                if is_datetime_in_interval(header.datetime, datetime_start, datetime_end):
                    for reading in headers_readings[header]:
                        if isinstance(reading, Reading):
                            reading.display(raw=namespace.raw, to_enumerate=namespace.enumerate)
                        elif isinstance(reading, CountedReading):
                            reading.display(raw=namespace.raw, to_enumerate=namespace.enumerate, decimal_places=namespace.calculate[0])
                        found_any = True
            if not found_any:
                logger.info('No readings was found on specified --datetime')
                return

        else:
            logger.error("Display target not selected (--header / --reading / --date)")
            return
        # !SECTION