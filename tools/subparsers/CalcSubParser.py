#pylint: disable=C0303 C0301 E0401 E0611

from argparse import _SubParsersAction, Namespace
from loguru import logger
from models.ReadableFile import ReadableFile
from models.Header import Header
from models.exceptions import InvalidResourceReductionError
from tools.Calculator import Calculator
from tools.FileParser import FileParser

class CalcSubParser:
    '''Calculations based on headers and readings'''

    @staticmethod
    def add_subparser(subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        check_subparser = subparsers.add_parser('calc', description='Checking incoming data or files against patterns')
        check_subparser.add_argument('-i', '--input', nargs=1, type=ReadableFile, required=True, help='Path to the file with readings')
        
        # NOTE - One of this targets must be specified
        check_subparser.add_argument('-vi', '--voltage-interval', action='store_true', help='Find minimal and maximal voltage')
        check_subparser.add_argument('-ac', '--acceleration', action='store_true', help='Calculate the accelerations')

        # NOTE - Modes of search and visualization
        check_subparser.add_argument('-d', '--date', nargs='+', type=str, help='Date on which to specify acceleration or voltage interval (specify two for the range) (dd.mm.yyyy)')
        check_subparser.add_argument('-m', '--minimal', nargs=1, type=int, help='Values below this will not be taken into account when searching for a voltage interval (default: 15)')
        check_subparser.add_argument('-a', '--accuracy', nargs=1, type=int, help='Number of decimal places of the displayed values (default: 2, max: 5)')
        return subparsers

    @staticmethod
    def run_calc(namespace : Namespace) -> None:
        '''Run if Calc subparser was called'''

        # SECTION - Validate and reduce readings before parsing
        resource_path = namespace.input[0].name

        time_check = FileParser.validate_readings_by_time(file_path=resource_path, log_success=False)
        pattern_check = FileParser.validate_readings_by_pattern(file_path=resource_path, log_success=False)
        
        if time_check and pattern_check:
            resource_path = FileParser.reduce_readings(resource_path)
        else:
            raise InvalidResourceReductionError
        # !SECTION

        # NOTE - Parse readings and calculate speed and voltage
        headers_readings = FileParser.parse_readings(file_path=namespace.input[0].name)
        headers_readings = Calculator.convert_readings(headers_readings)

        # NOTE - Check if count of --date args is wrong
        if namespace.date and len(namespace.date) > 2:
            logger.error("One or two dates can be passed with the --date argument")
            return

        # NOTE - Filling parameters with values or None if no arguments are used
        minimal_value = namespace.minimal[0] if namespace.minimal else 15
        date_start = Header.try_parse_date(namespace.date[0]) if namespace.date and len(namespace.date) >= 1 else None
        date_end = Header.try_parse_date(namespace.date[1]) if namespace.date and len(namespace.date) == 2 else None

        # NOTE - Set calculation accuracy (arg or default)
        if not namespace.accuracy:
            decimal_places = 2
        elif namespace.accuracy[0] <= 5 and namespace.accuracy[0] > 0:
            decimal_places = namespace.accuracy[0]
        else:
            logger.error("Used unavailable --accuracy, the value must be from 1 to 5 inclusive")
            return

        # SECTION - Processing targets: --voltage-interval
        if namespace.voltage_interval:
            voltage_interval = Calculator.find_voltage_interval(headers_readings, minimal_value, date_start, date_end)
            
            if voltage_interval is not None:
                print(f"Minimal voltage: {round(voltage_interval['min'], decimal_places)}v\nMaximal voltage: {round(voltage_interval['max'], decimal_places)}v")
            else:
                logger.info("No volt interval was found for these conditions")
                return

        elif namespace.acceleration:
            for header in headers_readings:
                enumeration = 1

                date_start = Header.try_parse_date(namespace.date[0]) if namespace.date and len(namespace.date) >= 1 else None
                date_end = Header.try_parse_date(namespace.date[1]) if namespace.date and len(namespace.date) == 2 else None

                if not Header.is_date_in_interval(header.date, date_start, date_end):
                    continue

                header.display(raw=False, to_enumerate=True)

                if len(headers_readings[header]) < 2:
                    print("    No speed change detected")
                    continue
                else:
                    for reading_index in range(len(headers_readings[header]) - 1):
                        first_reading = headers_readings[header][reading_index]
                        second_reading = headers_readings[header][reading_index + 1]
                        acceleration = Calculator.calculate_acceleration(first_reading.speed_kmh, first_reading.millis_passed, second_reading.speed_kmh, second_reading.millis_passed)
                        print(f"    [{enumeration}-{enumeration+1}] Acceleration: {round(acceleration, decimal_places)} m/s")
                        enumeration += 1

        else:
            logger.error("Calc mode not selected (--voltage-interval / --acceleration)")
            return
        # !SECTION