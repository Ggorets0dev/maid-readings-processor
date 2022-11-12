#pylint: disable=C0303 C0301 E0401 E0611

from argparse import _SubParsersAction, Namespace
from loguru import logger
from models.ReadableFile import ReadableFile
from models.Header import Header
from models.Reading import Reading
from models.CountedReading import CountedReading
from tools.additional_datetime_utils import try_parse_datetime, is_datetime_in_interval
from tools.Calculator import Calculator

class CalcSubParser:
    '''Calculations based on headers and readings'''

    # TODO - Average speed (km/h)
    # TODO - Travel time

    @staticmethod
    def add_subparser(subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        check_subparser = subparsers.add_parser('calc', description='Checking incoming data or files against patterns')
        check_subparser.add_argument('-i', '--input', nargs=1, type=ReadableFile, required=True, help='Path to the file with readings')
        
        # NOTE - One of this targets must be specified
        check_subparser.add_argument('-vi', '--voltage-interval', action='store_true', help='Find minimal and maximal voltage')
        check_subparser.add_argument('-ac', '--accelerations', action='store_true', help='Calculate and display all available accelerations')
        check_subparser.add_argument('-aa', '--average-acceleration', action='store_true', help='Calculate average speed boost (acceleration > 0)')
        check_subparser.add_argument('-ad', '--average-deceleration', action='store_true', help='Calculate average speed decrease (acceleration < 0)')

        # NOTE - Modes of search and visualization
        check_subparser.add_argument('-d', '--date-time', nargs='+', type=str, help='Date and time on which to specify acceleration or voltage interval (specify two for the range) (dd.mm.yyyy or dd.mm.yyyy-hh:mm:ss)')
        check_subparser.add_argument('-m', '--minimal', nargs=1, type=int, help='Values below this will not be taken into account when searching for a voltage interval (default: 15)')
        check_subparser.add_argument('-a', '--accuracy', nargs=1, type=int, help='Number of decimal places of the displayed values (default: 2, max: 5)')
        return subparsers

    @staticmethod
    def run_calc(namespace : Namespace) -> None:
        '''Run if Calc subparser was called'''

        resource_path = namespace.input[0].name

        # NOTE - Check if count of --date args is wrong
        if namespace.date_time and len(namespace.date_time) > 2:
            logger.error("One or two dates can be passed with the --date argument")
            return

        # NOTE - Filling parameters with values or None if no arguments are used
        minimal_value = namespace.minimal[0] if namespace.minimal else 15
        datetime_start = try_parse_datetime(namespace.date_time[0]) if namespace.date_time and len(namespace.date_time) >= 1 else None
        datetime_end = try_parse_datetime(namespace.date_time[1]) if namespace.date_time and len(namespace.date_time) == 2 else None

        # NOTE - Set calculation accuracy (arg or default=2)
        if not namespace.accuracy:
            decimal_places = 2
        elif namespace.accuracy[0] > 0 and namespace.accuracy[0] <= 5:
            decimal_places = namespace.accuracy[0]
        else:
            logger.error("Used unavailable --accuracy, the value must be from 1 to 5 inclusive")
            return

        # SECTION - Processing targets: --voltage-interval --all-accelerations --average-acceleration --average-deceleration
        if namespace.voltage_interval:
            voltage_interval = Calculator.find_voltage_interval(resource_path, minimal_value, datetime_start, datetime_end)
            
            if voltage_interval:
                print(f"Minimal voltage: {round(voltage_interval['min'], decimal_places)}v\nMaximal voltage: {round(voltage_interval['max'], decimal_places)}v")
            else:
                logger.info("No voltage interval was found for specified conditions")
                return

        # FIXME - Use until condition is maintained, not neighboring
        elif namespace.accelerations:
            last_header = None
            previous_reading = None
            current_reading = None
            displayed_readings_cnt = 0
            displayed_headers_cnt = 0
            skip_header = False
            
            with open(resource_path, 'r', encoding='UTF-8') as file_r:
                while True:
                    line = file_r.readline()
                    
                    if not line:
                        if displayed_readings_cnt == 0 and displayed_headers_cnt != 0:
                            print("     No speed change detected")
                        elif displayed_headers_cnt == 0:
                            logger.info("No accelerations and decelerations were found for specified conditions")
                        break
                    
                    elif Header.is_header(line):
                        if last_header and Header(line).datetime == last_header.datetime:
                            continue

                        elif not is_datetime_in_interval(Header(line).datetime, datetime_start, datetime_end):
                            skip_header = True
                            continue
                        else:
                            skip_header = False

                        if last_header and displayed_readings_cnt == 0:
                            print("     No speed change detected")
                        
                        last_header = Header(line)
                        last_header.display(raw=False, to_enumerate=True)
                        displayed_headers_cnt += 1
                        previous_reading = None
                        displayed_readings_cnt = 0
                    
                    elif Reading.is_reading(line):
                        if not skip_header:
                            current_reading = CountedReading(Reading(line), last_header.spokes_cnt, last_header.wheel_circ, last_header.max_voltage, last_header.save_delay)
                            if previous_reading:
                                acceleration = Calculator.calculate_acceleration(previous_reading.speed_kmh, previous_reading.millis_passed, current_reading.speed_kmh, current_reading.millis_passed)
                                print(f"     [{displayed_readings_cnt+1}-{displayed_readings_cnt+2}] Acceleration: {round(acceleration, 2)} m/s^2")
                                displayed_readings_cnt += 1
                            previous_reading = current_reading
        
        # FIXME - Use until condition is maintained, not neighboring
        elif namespace.average_acceleration:
            average_acceleration = Calculator.find_average_acceleration(file_path=resource_path, increase=True, datetime_start=datetime_start, datetime_end=datetime_end)

            if average_acceleration:
                print(f"Average acceleration: {round(average_acceleration, decimal_places)} m/s^2")
            else:
                logger.info("No accelerations were found for specified conditions")

        # FIXME - Use until condition is maintained, not neighboring    
        elif namespace.average_deceleration:
            average_deceleration = Calculator.find_average_acceleration(file_path=resource_path, increase=False, datetime_start=datetime_start, datetime_end=datetime_end)

            if average_deceleration:
                print(f"Average deceleration: {round(average_deceleration, decimal_places)} m/s^2")
            else:
                logger.info("No decelerations were found for specified conditions")

        else:
            logger.error("Calculation target not selected (--voltage-interval / --all-accelerations / --average-acceleration / --average-deceleration)")
            return
        # !SECTION