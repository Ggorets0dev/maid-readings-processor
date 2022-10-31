#pylint: disable=C0301 C0303 E0401 E0611

from argparse import _SubParsersAction, Namespace
from loguru import logger
from tools.FileParser import FileParser
from tools.Calculator import Calculator
from models.Header import Header
from models.Reading import Reading
from models.ReadableFile import ReadableFile
from models.CountedReading import CountedReading
from models.exceptions import InvalidResourceReductionError

class ShowSubParser:
    '''Output files or other data'''

    @staticmethod
    def add_subparser(subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        show_subparser = subparsers.add_parser('show', description='Displaying values on the screen without calculating any information')
        show_subparser.add_argument('-i', '--input', nargs=1, type=ReadableFile, required=True, help='Path to the file with readings')
        
        # NOTE - One of this targets must be specified
        show_subparser.add_argument('-he', '--header', action='store_true', help='Display target: headers')
        show_subparser.add_argument('-re', '--reading', action='store_true', help='Display target: readings')
        show_subparser.add_argument('-da', '--date', nargs='+', help='Display target: readings written in specified day (specify two for the range) (dd.mm.yyyy)')
        show_subparser.add_argument('-lc', '--line-count', action='store_true', help='Display number of lines in file')

        # NOTE - Modes of visualisation
        show_subparser.add_argument('--fix', action='store_true', help='Try to fix the file automatically')
        show_subparser.add_argument('-r', '--raw', action='store_true', help='Display values without visual processing')
        show_subparser.add_argument('-e', '--enumerate', action='store_true', help='Number displayed values')
        show_subparser.add_argument('-o', '--original', action='store_true', help='No line check and no file reducing (enabled by default)')
        show_subparser.add_argument('-c', '--calculate', nargs=1, type=int, help='Verify the number of pulses in km/h and the analog value in volts with CALCULATE decimal places (disabled by default)')
        return subparsers

    @staticmethod
    def run_show(namespace : Namespace) -> None:
        '''Run if Show subparser was called'''

        resource_path = namespace.input[0].name

        # NOTE - Processing targets: --line-count
        if namespace.line_count:
            print(f"Lines in requested file: {FileParser.count_lines(file_path=resource_path)}")
            return

        # NOTE - Validate and reducre readings if we dont use original file
        if not namespace.original:
            time_check = FileParser.validate_readings_by_time(file_path=resource_path, log_success=False)
            pattern_check = FileParser.validate_readings_by_pattern(file_path=resource_path, log_success=False)
            
            if time_check and pattern_check:
                resource_path = FileParser.reduce_readings(resource_path)
            else:
                raise InvalidResourceReductionError

        headers_readings = FileParser.parse_readings(file_path=resource_path, fix=namespace.fix)
        
        # NOTE - Use convertion of Reading to CountedReading with specified accuracy
        if namespace.calculate:
            if namespace.calculate[0] <= 5 and namespace.calculate[0] > 0:
                headers_readings = Calculator.convert_readings(headers_readings)
            else:
                logger.error("Calculation accuracy --calculate: maximal: 5, minimal: 1 (decimal places)")
                return

        # SECTION - Processing targets: --header --reading --date
        if namespace.header or namespace.reading:
            if namespace.header:
                for header in headers_readings:
                    header.display(raw=namespace.raw, to_enumerate=namespace.enumerate)
                        
            elif namespace.reading:
                for header in headers_readings:
                    for reading in headers_readings[header]:
                        if isinstance(reading, Reading):
                            reading.display(raw=namespace.raw, to_enumerate=namespace.enumerate)
                        elif isinstance(reading, CountedReading):
                            reading.display(raw=namespace.raw, to_enumerate=namespace.enumerate, decimal_places=namespace.calculate[0])

            
        elif namespace.date:
            if len(namespace.date) > 2:
                logger.error("One or two dates can be passed with the --date argument")
                return

            found_any = False

            date_start = Header.try_parse_date(namespace.date[0]) if len(namespace.date) >= 1 else None
            date_end = Header.try_parse_date(namespace.date[1]) if len(namespace.date) == 2 else None

            for header in headers_readings:
                if Header.is_date_in_interval(header.date, date_start, date_end):
                    found_any = True
                else:
                    continue

                if isinstance(headers_readings[header][0], Reading):
                    Reading.display_list(headers_readings[header], raw=namespace.raw, to_enumerate=namespace.enumerate)
                elif isinstance(headers_readings[header][0], CountedReading):
                    CountedReading.display_list(headers_readings[header], raw=namespace.raw, to_enumerate=namespace.enumerate, decimal_places=namespace.calculate[0])
            
            if not found_any:
                logger.info("No readings for requested date(s) were found")
                return

        else:
            logger.error("Display target not selected (--header / --reading / --date)")
            return
        # !SECTION