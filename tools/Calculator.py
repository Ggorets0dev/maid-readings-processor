import os
from datetime import datetime
from copy import copy
from models.exceptions import ResourceNotFoundError
from models.Header import Header
from models.CountedReading import CountedReading
from models.Reading import Reading
from tools.additional_datetime_utils import get_time, is_datetime_in_interval

class Calculator:
    '''Operations with Headers and Readings from file or memory'''

    @staticmethod
    def convert_readings(headers_readings : dict[Header, list[Reading]]) -> dict[Header, list[CountedReading]]:
        '''Convert list of Readings to list of CountedReadings'''
        for header in headers_readings:
            for i in range(len(headers_readings[header])):
                headers_readings[header][i] = CountedReading(headers_readings[header][i], header.spokes_cnt, header.wheel_circ, header.max_voltage, header.save_delay)
            for reading in headers_readings[header]:
                reading.time = get_time(header.datetime, reading.millis_passed)
        return headers_readings

    @staticmethod
    def get_voltage_interval(file_path : str, minimal_voltage : int, datetime_start : datetime, datetime_end : datetime) -> dict[str, float]:
        '''Find minimal and maximal voltage in requested file'''
        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path)

        interval = { 'min': 1000.0, 'max': -1.0 }
        skip_header = False
        last_header = None

        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()

                if not line:
                    break

                if Header.is_header(line):
                    last_header = Header(line)
                    skip_header = not is_datetime_in_interval(Header(line).datetime, datetime_start, datetime_end)
                
                elif Reading.is_reading(line) and not skip_header and last_header:
                    voltage_v = CountedReading.calculate_voltage(Reading(line).analog_voltage, last_header.max_voltage)  
                    if voltage_v >= minimal_voltage:
                        interval['min'], interval['max'] = min(interval['min'], voltage_v), max(interval['max'], voltage_v)
        
        if interval['min'] != 1000.0 and interval['max'] != -1.0: # * Check if it's still initial value
            return interval
        else:
            return {}

    @staticmethod
    def calculate_acceleration(first_speed_kmh : float, first_time_ms : float, second_speed_kmh : float, second_time_ms : float) -> float:
        '''Calculate acceleration for one pair (m/s^2)'''
        speed_change = (second_speed_kmh - first_speed_kmh) * 1000 / 3600
        time_change = abs(second_time_ms - first_time_ms) / 1000
        return speed_change / time_change
    
    @staticmethod
    def calculate_travel_distance(first_speed_kmh : float, first_time_ms : float, second_time_ms : float) -> float:
        '''Calculate the traveled distance for one pair (km)'''
        time_change = abs(second_time_ms - first_time_ms) / 1000
        travel_distance = (time_change / 60) * (first_speed_kmh / 60)
        return travel_distance

    @staticmethod
    def get_average_acceleration(file_path : str, find_increase : bool, datetime_start : datetime, datetime_end : datetime) -> float:
        '''Find average speed boost or decrease (m/s^2)'''
        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path)

        acceleration_sum = acceleration_cnt = 0
        increase = decrease = skip_header = False
        last_header = first_reading = last_reading = buffer_reading = None

        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()
                
                if not line:
                    if first_reading and last_reading:
                        acceleration = Calculator.calculate_acceleration(first_reading.speed_kmh, first_reading.millis_passed, last_reading.speed_kmh, last_reading.millis_passed)
                        if (find_increase and acceleration > 0) or (not find_increase and acceleration < 0):
                            acceleration_sum += acceleration
                            acceleration_cnt += 1
                    break
                
                elif Header.is_header(line):
                    if first_reading and last_reading:
                        acceleration = Calculator.calculate_acceleration(first_reading.speed_kmh, first_reading.millis_passed, last_reading.speed_kmh, last_reading.millis_passed)
                        if (find_increase and acceleration > 0) or (not find_increase and acceleration < 0):
                            acceleration_sum += acceleration
                            acceleration_cnt += 1

                    skip_header = not is_datetime_in_interval(Header(line).datetime, datetime_start, datetime_end)
                    
                    last_header = Header(line)
                    first_reading = last_reading = buffer_reading = None
                    increase = decrease = False
                
                elif Reading.is_reading(line) and not skip_header and last_header:
                    if first_reading:
                        buffer_reading = CountedReading(Reading(line), last_header.spokes_cnt, last_header.wheel_circ, last_header.max_voltage, last_header.save_delay)
                        
                        last_reading = copy(first_reading) if not last_reading else last_reading
                        
                        if ((buffer_reading.speed_kmh > last_reading.speed_kmh) and decrease) or ((buffer_reading.speed_kmh < last_reading.speed_kmh) and increase):
                            acceleration = Calculator.calculate_acceleration(first_reading.speed_kmh, first_reading.millis_passed, last_reading.speed_kmh, last_reading.millis_passed)
                            if (find_increase and acceleration > 0) or (not find_increase and acceleration < 0):
                                acceleration_sum += acceleration
                                acceleration_cnt += 1
                            first_reading, last_reading = copy(last_reading), copy(buffer_reading)
                            increase = decrease = False
                        
                        elif buffer_reading.speed_kmh == last_reading.speed_kmh:
                            first_reading = copy(buffer_reading)
                        
                        else:
                            last_reading = copy(buffer_reading)
                            increase = True if not(increase and decrease) and (last_reading.speed_kmh > first_reading.speed_kmh) else increase
                            decrease = True if not(increase and decrease) and (last_reading.speed_kmh < first_reading.speed_kmh) else decrease
                    else:
                        first_reading = CountedReading(Reading(line), last_header.spokes_cnt, last_header.wheel_circ, last_header.max_voltage, last_header.save_delay)

        if acceleration_sum != 0 and acceleration_cnt != 0:
            return acceleration_sum / acceleration_cnt
        else:
            return 0

    @staticmethod
    def get_average_speed(file_path : str, datetime_start : datetime, datetime_end : datetime) -> float:
        '''Find average speed (km/h)'''
        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path)
        
        speed_sum = speed_cnt = 0
        last_header = None
        skip_header = False

        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()

                if not line:
                    break

                elif Header.is_header(line):
                    last_header = Header(line)
                    skip_header = not is_datetime_in_interval(last_header.datetime, datetime_start, datetime_end)

                elif Reading.is_reading(line) and not skip_header and last_header:
                    current_reading = CountedReading(Reading(line), last_header.spokes_cnt, last_header.wheel_circ, last_header.max_voltage, last_header.save_delay)
                    speed_cnt += 1
                    speed_sum += current_reading.speed_kmh
            
        if speed_cnt != 0 and speed_sum != 0:
            return speed_sum / speed_cnt
        else:
            return 0

    @staticmethod
    def get_travel_time(file_path : str, datetime_start : datetime, datetime_end : datetime) -> float:
        '''Find travel time (sec)'''
        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path)

        time_sum_sec = 0
        current_header = last_reading = None
        skip_header = False

        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()

                if not line:
                    if last_reading:
                        time_sum_sec += (last_reading.millis_passed / 1000)
                    break

                elif Header.is_header(line):
                    if last_reading:
                        time_sum_sec += (last_reading.millis_passed / 1000)

                    current_header = Header(line)
                    last_reading = None
                    skip_header = not is_datetime_in_interval(current_header, datetime_start, datetime_end)
                                
                elif Reading.is_reading(line) and not skip_header:
                    last_reading = Reading(line)
        
        return time_sum_sec

    @staticmethod
    def get_travel_distance(file_path: str, datetime_start : datetime, datetime_end : datetime) -> float:
        '''Find travel distance'''
        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path)

        travel_distance_km = 0
        current_header = current_reading = last_reading = None
        skip_header = False

        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()

                if not line:
                    if last_reading and current_reading:
                        travel_distance_km += Calculator.calculate_travel_distance(current_reading.speed_kmh, current_reading.millis_passed, last_reading.millis_passed)
                    break

                elif Header.is_header(line):
                    if last_reading and current_reading:
                        travel_distance_km += Calculator.calculate_travel_distance(current_reading.speed_kmh, current_reading.millis_passed, last_reading.millis_passed)
                    
                    current_header = Header(line)
                    skip_header = not is_datetime_in_interval(current_header.datetime, datetime_start, datetime_end)
                    current_reading, last_reading = None, CountedReading(Reading.create_empty(), current_header.spokes_cnt, current_header.wheel_circ, current_header.max_voltage, current_header.save_delay)

                elif Reading.is_reading(line) and not skip_header and current_header:
                    current_reading = CountedReading(Reading(line), current_header.spokes_cnt, current_header.wheel_circ, current_header.max_voltage, current_header.save_delay)

                    if last_reading and current_reading:
                        travel_distance_km += Calculator.calculate_travel_distance(current_reading.speed_kmh, current_reading.millis_passed, last_reading.millis_passed)

                    last_reading = copy(current_reading)

        return travel_distance_km
    