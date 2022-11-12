# pylint: disable=E0401 E0611

import os
from datetime import datetime
from models.exceptions import ResourceNotFoundError
from models.Header import Header
from models.CountedReading import CountedReading
from models.Reading import Reading
from tools.additional_datetime_utils import set_time, is_datetime_in_interval

class Calculator:
    '''Operations with Headers and Readings from file or memory'''

    @staticmethod
    def convert_readings(headers_readings : dict[Header, list[Reading]]) -> dict[Header, list[CountedReading]]:
        '''Convert list of Readings to list of CountedReadings'''
        for header in headers_readings:
            for i in range(len(headers_readings[header])):
                headers_readings[header][i] = CountedReading(headers_readings[header][i], header.spokes_cnt, header.wheel_circ, header.max_voltage, header.save_delay)
            headers_readings[header] = set_time(header.datetime, headers_readings[header])
        return headers_readings

    @staticmethod
    def find_voltage_interval(file_path : str, minimal_voltage : int, datetime_start : datetime, datetime_end : datetime) -> dict[str, float]:
        '''Find minimal and maximal voltage in requested file'''
        interval = { 'min': 1000.0, 'max': -1.0 }
        line = ''
        use_header = False
        last_header = None

        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path)

        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()

                if not line:
                    break

                elif line  == '\n' or line  == '':
                    continue

                if Header.is_header(line):
                    last_header = Header(line)
                    use_header = is_datetime_in_interval(Header(line).datetime, datetime_start, datetime_end)
                
                elif Reading.is_reading(line):
                    if last_header and use_header:
                        voltage_v = CountedReading.calculate_voltage(Reading(line).analog_voltage, last_header.max_voltage)  
                        if voltage_v >= minimal_voltage:
                            interval['min'] = min(interval['min'], voltage_v)
                            interval['max'] = max(interval['max'], voltage_v)
        
        if interval['min'] != 1000.0 and interval['max'] != -1.0: # * Check if it's still initial value
            return interval
        else:
            return None

    @staticmethod
    def calculate_acceleration(first_speed_kmh : float, first_time_ms : float, second_speed_kmh : float, second_time_ms : float) -> float:
        '''Calculate acceleration between to speeds (m/s^2)'''
        delta_speed = (second_speed_kmh - first_speed_kmh) * 1000 / 3600
        delta_time = (second_time_ms - first_time_ms) / 1000

        return delta_speed / delta_time

    @staticmethod
    def find_average_acceleration(file_path : str, increase : bool, datetime_start : datetime, datetime_end : datetime) -> float:
        '''Find average speed boost or decrease (m/s^2)'''
        last_header = None
        previous_reading = None
        current_reading = None
        acceleration_cnt = 0
        acceleration_sum = 0
        skip_header = False
        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()

                if not line:
                    break

                elif Header.is_header(line):
                    if last_header and Header(line).datetime == last_header.datetime:
                        continue

                    elif not is_datetime_in_interval(Header(line).datetime, datetime_start, datetime_end):
                        skip_header = True
                        continue
                    else:
                        skip_header = False

                    last_header = Header(line)
                    previous_reading = None

                elif Reading.is_reading(line):
                    if not skip_header:
                        current_reading = CountedReading(Reading(line), last_header.spokes_cnt, last_header.wheel_circ, last_header.max_voltage, last_header.save_delay)
                        if previous_reading:
                            acceleration = Calculator.calculate_acceleration(previous_reading.speed_kmh, previous_reading.millis_passed, current_reading.speed_kmh, current_reading.millis_passed)
                            if acceleration > 0 and increase:
                                acceleration_cnt += 1
                                acceleration_sum += acceleration
                            elif acceleration < 0 and not increase:
                                acceleration_cnt += 1
                                acceleration_sum += acceleration
                        previous_reading = current_reading

        if acceleration_cnt != 0 and acceleration_sum != 0:
            return acceleration_sum / acceleration_cnt
        else:
            return None