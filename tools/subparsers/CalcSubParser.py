#pylint: disable=C0303 C0301 E0401 E0611

from argparse import _SubParsersAction, Namespace
from loguru import logger
from models.ReadableFile import ReadableFile
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
        check_subparser.add_argument('-e', '--every', action='store_true', help='Display accelerations between all readings')
        check_subparser.add_argument('-m', '--minimal', nargs=1, type=int, help='Values below this will not be taken into account when searching for a voltage interval (default: 15)')
        check_subparser.add_argument('-a', '--accuracy', nargs=1, type=int, help='Number of decimal places of the displayed values (default: 2, max: 5)')
        return subparsers

    @staticmethod
    def run_calc(namespace : Namespace) -> None:
        '''Run if Calc subparser was called'''

        # NOTE - Parse readings and calculate speed and voltage
        headers_readings = FileParser.parse_readings(file_path=namespace.input[0].name)
        headers_readings = Calculator.convert_readings(headers_readings, decimal_places=5)

        # NOTE - Set display and calculation accuracy (decimal places)
        if not namespace.accuracy:
            decimal_places = 2
        
        elif namespace.accuracy[0] <= 5 and namespace.accuracy[0] > 0:
            decimal_places = namespace.accuracy[0]

        else:
            logger.error("Calculation and displaying --accuracy: maximal: 5, minimal: 1 (decimal places)")
            return

        # SECTION - Processing targets: --voltage-interval
        if namespace.voltage_interval:
            if namespace.minimal:
                voltage_interval = Calculator.find_voltage_interval(headers_readings, minimal_voltage=namespace.minimal[0])
            else:
                voltage_interval = Calculator.find_voltage_interval(headers_readings)
            
            if voltage_interval is not None:
                print(f"Minimal voltage: {round(voltage_interval['min'], decimal_places)}v\nMaximal voltage: {round(voltage_interval['max'], decimal_places)}v")

            else:
                logger.error("Failed to find the volt interval by condition")
                return

        elif namespace.acceleration:
            if namespace.every:
                for header in headers_readings:
                    enumeration = 1
                    header.display(raw=False, to_enumerate=True)
                    for reading_index in range(len(headers_readings[header]) - 1):
                        first_reading = headers_readings[header][reading_index]
                        second_reading = headers_readings[header][reading_index + 1]
                        acceleration = Calculator.calculate_acceleration(first_reading.speed_kmh, first_reading.millis_passed, second_reading.speed_kmh, second_reading.millis_passed)
                        print(f"    [{enumeration}-{enumeration+1}] Acceleration: {round(acceleration, decimal_places)} m/s")
                        enumeration += 1
            else:
                logger.error("Selection mode for the --acceleration target is not selected")
                return

        else:
            logger.error("Calc mode not selected (--voltage-interval or --acceleration)")
            return
        # !SECTION