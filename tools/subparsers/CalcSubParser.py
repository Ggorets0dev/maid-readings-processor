'''CalcSubParser location'''

from copy import copy
from datetime import datetime, timedelta
from argparse import _SubParsersAction, Namespace
from colorama import Fore, Style
from loguru import logger
from models.ReadableFile import ReadableFile
from models.Header import Header
from models.Reading import Reading
from models.Config import Config
from models.CountedReading import CountedReading
from tools.Calculator import Calculator
from tools.additional_datetime_utils import try_parse_datetime, get_time
from tools.display_utils import Color, CalculatedValueOutput

class CalcSubParser:
    '''Calculations based on headers and readings'''

    @classmethod
    def add_subparser(cls, subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        calc_subparser = subparsers.add_parser('calc', description='Checking incoming data or files against patterns')
        calc_subparser.add_argument('-i', '--input', nargs=1, type=ReadableFile, required=True, help='Path to the file with readings')
        
        # NOTE - One of this targets must be specified
        calc_subparser.add_argument('-vi', '--voltage-interval', action='store_true', help='Find minimal and maximal voltage')
        calc_subparser.add_argument('-ac', '--accelerations', action='store_true', help='Calculate and display all available accelerations')
        calc_subparser.add_argument('-aa', '--average-acceleration', action='store_true', help='Calculate average speed boost (acceleration > 0)')
        calc_subparser.add_argument('-ad', '--average-deceleration', action='store_true', help='Calculate average speed decrease (acceleration < 0)')
        calc_subparser.add_argument('-as', '--average-speed', action='store_true', help='Calculate average speed')
        calc_subparser.add_argument('-tt', '--travel-time', action='store_true', help='Find travel time in minutes')
        calc_subparser.add_argument('-td', '--travel-distance', action='store_true', help='Number of kilometers traveled')

        # NOTE - Modes of search and visualization
        calc_subparser.add_argument('-d', '--date-time', nargs='+', type=str, help='Date and time to filter values (specify two for the interval) (dd.mm.yyyy or dd.mm.yyyy-hh:mm:ss)')
        calc_subparser.add_argument('-a', '--accuracy', nargs=1, type=int, help='Number of decimal places of the displayed values (min: 1, max: 5, default: 2)')
        
        cls.SUBPARSER = calc_subparser
        return subparsers

    @classmethod
    def run_calc(cls, namespace : Namespace) -> None:
        '''Run if Calc subparser was called'''
        resource_path = namespace.input[0].name
        decimal_places = namespace.accuracy[0] if namespace.accuracy and 0 < namespace.accuracy[0] <= 5 else 2
        config = Config.collect()

        # NOTE - Check the correctness of the passed arguments --date-time
        if (namespace.date_time and len(namespace.date_time) <= 2) or not namespace.date_time:
            datetime_start = try_parse_datetime(namespace.date_time[0]) if namespace.date_time and len(namespace.date_time) >= 1 else datetime(2000, 1, 1)
            datetime_end = try_parse_datetime(namespace.date_time[1], last_day=True) if namespace.date_time and len(namespace.date_time) == 2 else datetime(3000, 1, 1)
        else:
            logger.error("One or two dates can be passed with the --date-time argument")
            return

        # SECTION - Processing targets: --voltage-interval --all-accelerations --average-acceleration --average-deceleration --average-speed --travel-time --travel-distance
        if namespace.voltage_interval:
            voltage_interval = Calculator.get_voltage_interval(resource_path, datetime_start, datetime_end, config.minimal_voltage_search)
            
            if len(voltage_interval) != 0:
                CalculatedValueOutput('Minimal voltage', str(round(voltage_interval['min'], decimal_places)), 'v').display()
                CalculatedValueOutput('Maximal voltage', str(round(voltage_interval['max'], decimal_places)), 'v').display()
            else:
                logger.info("No voltage interval was found for specified conditions")
                return

        elif namespace.accelerations:
            displayed_headers_cnt = displayed_accelerations_cnt = 0
            increase = decrease = False
            current_header = first_reading = last_reading = buffer_reading = None
            last_header = Header.create_empty()

            with open(resource_path, 'r', encoding='UTF-8') as file_read:
                while True:
                    line = file_read.readline()
                    
                    if not line:
                        if first_reading and last_reading:
                            CalcSubParser.show_acceleration(first_reading, last_reading, current_header, decimal_places)
                            displayed_accelerations_cnt += 1

                        elif displayed_accelerations_cnt == 0 and displayed_headers_cnt != 0:
                            Color.cprint(msg="     No speed change detected", fore=Fore.RED, style=Style.BRIGHT)
                        
                        elif displayed_headers_cnt == 0:
                            logger.info("No accelerations and decelerations were found for specified conditions")
                        break
                    
                    elif Header.is_header(line):
                        if first_reading and last_reading:
                            CalcSubParser.show_acceleration(first_reading, last_reading, current_header, decimal_places)
                            displayed_accelerations_cnt += 1

                        elif current_header and displayed_accelerations_cnt == 0:
                            Color.cprint(msg="     No speed change detected", fore=Fore.RED, style=Style.BRIGHT)
                        
                        current_header = Header(line)
                        
                        if current_header.datetime > datetime_end:
                            break
                        elif current_header.datetime.date() != last_header.datetime.date():
                            current_header.display(time=False)
                        
                        displayed_headers_cnt += 1
                        displayed_accelerations_cnt = 0
                        first_reading = last_reading = buffer_reading = None
                        increase = decrease = False
                        last_header = copy(current_header)
                    
                    elif Reading.is_reading(line) and current_header:
                        reading = Reading(line)
                        reading_datetime = current_header.datetime + timedelta(milliseconds=reading.millis_passed)

                        if reading_datetime < datetime_start:
                            continue
                        elif reading_datetime > datetime_end:
                            if first_reading and last_reading:
                                CalcSubParser.show_acceleration(first_reading, last_reading, current_header, decimal_places)
                                displayed_accelerations_cnt += 1
                            elif current_header and displayed_accelerations_cnt == 0:
                                Color.cprint(msg="     No speed change detected", fore=Fore.RED, style=Style.BRIGHT)
                            break


                        if first_reading:
                            buffer_reading = CountedReading(Reading(line), current_header.spokes_cnt, current_header.wheel_circ, current_header.max_voltage, current_header.save_delay)
                            last_reading = copy(first_reading) if not last_reading else last_reading
                            
                            if ((buffer_reading.speed_kmh > last_reading.speed_kmh) and decrease) or ((buffer_reading.speed_kmh < last_reading.speed_kmh) and increase):
                                CalcSubParser.show_acceleration(first_reading, last_reading, current_header, decimal_places)
                                displayed_accelerations_cnt += 1
                                first_reading, last_reading = copy(last_reading), copy(buffer_reading)
                                increase = decrease = False
                            
                            elif buffer_reading.speed_kmh == last_reading.speed_kmh:
                                first_reading = copy(buffer_reading)
                            
                            else:
                                last_reading = copy(buffer_reading)
                                increase = True if not(increase and decrease) and (last_reading.speed_kmh > first_reading.speed_kmh) else increase
                                decrease = True if not(increase and decrease) and (last_reading.speed_kmh < first_reading.speed_kmh) else decrease

                        else:
                            first_reading = CountedReading(Reading(line), current_header.spokes_cnt, current_header.wheel_circ, current_header.max_voltage, current_header.save_delay)

        elif namespace.average_acceleration:
            average_acceleration = Calculator.get_average_acceleration(file_path=resource_path, find_increase=True, datetime_start=datetime_start, datetime_end=datetime_end)

            if average_acceleration != 0:
                CalculatedValueOutput('Average acceleration', str(round(average_acceleration, decimal_places)), 'm/s^2').display()
            else:
                logger.info("No accelerations were found for specified conditions")
 
        elif namespace.average_deceleration:
            average_deceleration = Calculator.get_average_acceleration(file_path=resource_path, find_increase=False, datetime_start=datetime_start, datetime_end=datetime_end)

            if average_deceleration != 0:
                CalculatedValueOutput('Average deceleration', str(round(average_deceleration, decimal_places)), 'm/s^2').display()
            else:
                logger.info("No decelerations were found for specified conditions")

        elif namespace.average_speed:
            average_speed = Calculator.get_average_speed(file_path=resource_path, datetime_start=datetime_start, datetime_end=datetime_end)

            if average_speed !=0:
                CalculatedValueOutput('Average speed', str(round(average_speed, decimal_places)), 'km/h').display()
            else:
                logger.info("No speed readings were found for specified conditions")
        
        elif namespace.travel_time:
            travel_time_sec = Calculator.get_travel_time(file_path=resource_path, datetime_start=datetime_start, datetime_end=datetime_end)

            if travel_time_sec != 0:
                CalculatedValueOutput('Travel time', str(round(travel_time_sec / 60, decimal_places)), 'min').display()
            else:
                logger.info("No travel time was found for specified conditions")

        elif namespace.travel_distance:
            travel_distance_km = Calculator.get_travel_distance(file_path=resource_path, datetime_start=datetime_start, datetime_end=datetime_end)

            if travel_distance_km != 0:
                CalculatedValueOutput('Travel distance', str(round(travel_distance_km, decimal_places)), 'km').display()
            else:
                logger.info("No travel distance was found for specified conditions")

        else:
            logger.error("Calculation target not selected (--voltage-interval / --all-accelerations / --average-acceleration / --average-deceleration / --average-speed / --travel-time / --travel-distance)")
            cls.SUBPARSER.print_help()
        # !SECTION

    @staticmethod
    def show_acceleration(first_reading : CountedReading, last_reading : CountedReading, current_header : Header, decimal_places : int) -> None:
        '''Output of acceleration between two CountedReading'''
        acceleration = Calculator.calculate_acceleration(first_reading.speed_kmh, first_reading.millis_passed, last_reading.speed_kmh, last_reading.millis_passed)
        first_reading.time = get_time(current_header.datetime, first_reading.millis_passed)
        last_reading.time = get_time(current_header.datetime, last_reading.millis_passed)
        
        acceleration_color = Fore.GREEN if acceleration > 0 else (Fore.YELLOW if acceleration == 0 else Fore.RED)

        time_colored = Color.colorize(msg=f"[{first_reading.time.strftime('%H:%M:%S:%f')} --> {last_reading.time.strftime('%H:%M:%S:%f')}]", fore=Fore.CYAN, style=Style.BRIGHT)
        acceleration_colored = Color.colorize(msg=str(round(acceleration, decimal_places)), fore=acceleration_color, style=Style.BRIGHT)

        print(f"     {time_colored} Acceleration: {acceleration_colored} m/s^2")
        