#pylint: disable=C0303  C0301 E0401

from argparse import _SubParsersAction, Namespace, FileType
from models.Header import Header

class CalcSubParser:
    '''Calculations based on headers and readings'''

    @staticmethod
    def add_subparser(subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        check_subparser = subparsers.add_parser('calc', description='Checking incoming data or files against patterns')
        check_subparser.add_argument('-i', '--input', nargs=1, type=FileType(encoding='UTF-8'), required=True, help='Path to the file with readings')
        check_subparser.add_argument('-p', '--pattern', action='store_true', help='Check that each line matches the header or reading pattern')
        check_subparser.add_argument('-t', '--time', action='store_true', help='Check whether each next date/time is later than the previous ones')
        return subparsers

    @staticmethod
    def run_check(namespace : Namespace) -> None:
        '''Run if Calc subparser was called'''
        pass

    @staticmethod
    def calculate_speed(impulse_cnt : int, config : Header, decimal_places : int) -> float:
        '''Calculation of speed in km/h based on the number of pulses and configuration from the header'''
        if impulse_cnt != 0:
            speed = (impulse_cnt / config.spokes_cnt * config.wheel_circ / 1_000_000) * (60 * 60 / config.save_delay)
            return round(speed, decimal_places)
        else:
            return 0.0

    @staticmethod
    def calculate_voltage(analog_voltage : int, config : Header, decimal_places : int) -> float:
        '''Conversion of analog value to real volts'''
        vin = analog_voltage * config.max_voltage / 1023
        if vin >= 5:
            return round(vin, decimal_places)
        else:
            return 0.0
        