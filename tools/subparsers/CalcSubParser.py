#pylint: disable=C0303 C0301 E0401 E0611

from copy import copy
from datetime import datetime
from argparse import _SubParsersAction, Namespace
from colorama import Fore, Style
from loguru import logger
from models.ReadableFile import ReadableFile
from models.Header import Header
from models.Reading import Reading
from models.CountedReading import CountedReading
from tools.Calculator import Calculator
from tools.additional_datetime_utils import try_parse_datetime, is_datetime_in_interval, get_time
from tools.text_formatting_utils import cprint, colorize

class CalcSubParser:
    '''Calculations based on headers and readings'''

    # TODO - Travel distance

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
        check_subparser.add_argument('-as', '--average-speed', action='store_true', help='Calculate average speed')
        # check_subparser.add_argument('-td', '--travel-distance', action='store_true', help='Number of kilometers traveled')
        check_subparser.add_argument('-tt', '--travel-time', action='store_true', help='Find travel time in minutes')

        # NOTE - Modes of search and visualization
        check_subparser.add_argument('-d', '--datetime', nargs='+', type=str, help='Date and time on which to specify acceleration or voltage interval (specify two for the range) (dd.mm.yyyy or dd.mm.yyyy-hh:mm:ss)')
        check_subparser.add_argument('-m', '--minimal', nargs=1, type=int, help='Values below this will not be taken into account when searching for a voltage interval (default: 15)')
        check_subparser.add_argument('-a', '--accuracy', nargs=1, type=int, help='Number of decimal places of the displayed values (min: 1, max: 5, default: 2)')
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
        datetime_start = try_parse_datetime(namespace.date_time[0]) if namespace.date_time and len(namespace.date_time) >= 1 else datetime(2000, 1, 1)
        datetime_end = try_parse_datetime(namespace.date_time[1]) if namespace.date_time and len(namespace.date_time) == 2 else datetime(3000, 1, 1)

        # NOTE - Set calculation accuracy (arg or default=2)
        if not namespace.accuracy:
            decimal_places = 2
        elif namespace.accuracy[0] > 0 and namespace.accuracy[0] <= 5:
            decimal_places = namespace.accuracy[0]
        else:
            logger.error("Used unavailable --accuracy, the value must be from 1 to 5 inclusive")
            return

        # SECTION - Processing targets: --voltage-interval --all-accelerations --average-acceleration --average-deceleration --average-speed --travel-time --travel-distance
        if namespace.voltage_interval:
            voltage_interval = Calculator.get_voltage_interval(resource_path, minimal_value, datetime_start, datetime_end)
            
            if len(voltage_interval) != 0:
                cprint(msg=f"Minimal voltage: {round(voltage_interval['min'], decimal_places)}v\nMaximal voltage: {round(voltage_interval['max'], decimal_places)}v", fore=Fore.WHITE, style=Style.BRIGHT)
            else:
                logger.info("No voltage interval was found for specified conditions")
                return

        # FIXME - Use until condition is maintained, not neighboring
        elif namespace.accelerations:
            displayed_readings_cnt = 0
            displayed_headers_cnt = 0
            last_header = None
            first_reading = None
            last_reading = None
            buffer_reading = None
            skip_header = False
            increase = False
            decrease = False

            with open(resource_path, 'r', encoding='UTF-8') as file_r:
                while True:
                    line = file_r.readline()
                    
                    if not line:
                        if first_reading and last_reading:
                            CalcSubParser.show_acceleration(first_reading, last_reading, last_header, decimal_places)
                            displayed_readings_cnt += 1
                        elif displayed_readings_cnt == 0 and displayed_headers_cnt != 0:
                            cprint(msg="     No speed change detected", fore=Fore.RED, style=Style.BRIGHT)
                        elif displayed_headers_cnt == 0:
                            logger.info("No accelerations and decelerations were found for specified conditions")
                        break
                    
                    elif Header.is_header(line):
                        if first_reading and last_reading:
                            CalcSubParser.show_acceleration(first_reading, last_reading, last_header, decimal_places)
                            displayed_readings_cnt += 1
                        
                        if last_header and Header(line).datetime == last_header.datetime:
                            continue
                        elif not is_datetime_in_interval(Header(line).datetime, datetime_start, datetime_end):
                            skip_header = True
                            continue
                        else:
                            skip_header = False

                        if last_header and displayed_readings_cnt == 0:
                            cprint(msg="     No speed change detected", fore=Fore.RED, style=Style.BRIGHT)
                        
                        last_header = Header(line)
                        last_header.display(time=False)
                        displayed_headers_cnt += 1
                        displayed_readings_cnt = 0
                        first_reading = None
                        last_reading = None
                        buffer_reading = None
                    
                    elif Reading.is_reading(line):
                        if not skip_header and last_header:
                            if first_reading:
                                buffer_reading = CountedReading(Reading(line), last_header.spokes_cnt, last_header.wheel_circ, last_header.max_voltage, last_header.save_delay)
                                
                                if ((buffer_reading.speed_kmh > first_reading.speed_kmh) and decrease) or ((buffer_reading.speed_kmh < first_reading.speed_kmh) and increase):
                                    CalcSubParser.show_acceleration(first_reading, buffer_reading, last_header, decimal_places)
                                    displayed_readings_cnt += 1
                                    first_reading = copy(buffer_reading)
                                
                                else:
                                    last_reading = copy(buffer_reading)

                                    if (buffer_reading.speed_kmh > first_reading.speed_kmh):
                                        increase = True

                                    elif (buffer_reading.speed_kmh < first_reading.speed_kmh):
                                        decrease = True

                            else:
                                first_reading = CountedReading(Reading(line), last_header.spokes_cnt, last_header.wheel_circ, last_header.max_voltage, last_header.save_delay)

        
        # FIXME - Use until condition is maintained, not neighboring
        elif namespace.average_acceleration:
            average_acceleration = Calculator.get_average_acceleration(file_path=resource_path, increase=True, datetime_start=datetime_start, datetime_end=datetime_end)

            if average_acceleration != 0:
                cprint(msg=f"Average acceleration: {round(average_acceleration, decimal_places)} m/s^2", fore=Fore.WHITE, style=Style.BRIGHT)
            else:
                logger.info("No accelerations were found for specified conditions")

        # FIXME - Use until condition is maintained, not neighboring    
        elif namespace.average_deceleration:
            average_deceleration = Calculator.get_average_acceleration(file_path=resource_path, increase=False, datetime_start=datetime_start, datetime_end=datetime_end)

            if average_deceleration != 0:
                cprint(msg=f"Average deceleration: {round(average_deceleration, decimal_places)} m/s^2", fore=Fore.WHITE, style=Style.BRIGHT)
            else:
                logger.info("No decelerations were found for specified conditions")

        elif namespace.average_speed:
            average_speed = Calculator.get_average_speed(file_path=resource_path, datetime_start=datetime_start, datetime_end=datetime_end)

            if average_speed !=0 :
                cprint(msg=f"Average speed: {round(average_speed, decimal_places)} km/h", fore=Fore.WHITE, style=Style.BRIGHT)
            else:
                logger.info("No speed readings were found for specified conditions")
        
        elif namespace.travel_time:
            travel_time_sec = Calculator.get_travel_time(file_path=resource_path, datetime_start=datetime_start, datetime_end=datetime_end)

            if travel_time_sec != 0:
                cprint(msg=f"Travel time: {round(travel_time_sec / 60, decimal_places)} min", fore=Fore.WHITE, style=Style.BRIGHT)
            else:
                logger.info("No travel time was found for specified conditions")

        else:
            logger.error("Calculation target not selected (--voltage-interval / --all-accelerations / --average-acceleration / --average-deceleration / --average-speed / --travel-time / --travel-distance)")
            return
        # !SECTION

    @staticmethod
    def show_acceleration(first_reading : CountedReading, last_reading : CountedReading, last_header : Header, decimal_places : int) -> None:
        '''Output of acceleration between two CountedReading'''
        acceleration = Calculator.calculate_acceleration(first_reading.speed_kmh, first_reading.millis_passed, last_reading.speed_kmh, last_reading.millis_passed)
        first_reading.time = get_time(last_header.datetime, first_reading.millis_passed)
        last_reading.time = get_time(last_header.datetime, last_reading.millis_passed)
        
        acceleration_color = Fore.GREEN if acceleration > 0 else (Fore.YELLOW if acceleration == 0 else Fore.RED)

        time_colored = colorize(msg=f"[{first_reading.time.strftime('%H:%M:%S:%f')} --> {last_reading.time.strftime('%H:%M:%S:%f')}]", fore=Fore.CYAN, style=Style.BRIGHT)
        acceleration_colored = colorize(msg=str(round(acceleration, decimal_places)), fore=acceleration_color, style=Style.BRIGHT)

        print(f"     {time_colored} Acceleration: {acceleration_colored} m/s^2")
        