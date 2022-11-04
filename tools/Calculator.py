# pylint: disable=E0401 E0611

from datetime import datetime
from models.Header import Header
from models.CountedReading import CountedReading
from models.Reading import Reading
from tools.additional_datetime_utils import set_time, is_datetime_in_interval

class Calculator:
    '''Operations with readings got from module'''

    @staticmethod
    def convert_readings(headers_readings : dict[Header, list[Reading]]) -> dict[Header, list[CountedReading]]:
        '''Convert list of Readings to list of CountedReadings'''
        for header in headers_readings:
            for i in range(len(headers_readings[header])):
                headers_readings[header][i] = CountedReading(headers_readings[header][i], header.spokes_cnt, header.wheel_circ, header.max_voltage, header.save_delay)
            headers_readings[header] = set_time(header.datetime, headers_readings[header])
        return headers_readings
        

    @staticmethod
    def find_voltage_interval(headers_readings : dict[Header, list[CountedReading]], minimal_voltage : int, datetime_start : datetime, datetime_end : datetime) -> dict[str, float]:
        '''Find minimal and maximal voltage in all CountedReadings'''
        interval = { 'min': 1000.0, 'max': 0.0 }
        
        for header in headers_readings:

            if not is_datetime_in_interval(header.datetime, datetime_start, datetime_end):
                continue

            for reading in headers_readings[header]:
                if reading.voltage_v >= minimal_voltage:
                    interval['min'] = min(interval['min'], reading.voltage_v)
                    interval['max'] = max(interval['max'], reading.voltage_v)
        
        if interval['min'] != 1000.0: # * Check if it's still initial value
            return interval
        else:
            return None

    @staticmethod
    def calculate_acceleration(first_speed_kmh : float, first_time_ms : float, second_speed_kmh : float, second_time_ms : float) -> float:
        '''Calculate acceleration between to speeds (m/s)'''
        delta_speed = (second_speed_kmh - first_speed_kmh) * 1000 / 3600
        delta_time = (second_time_ms - first_time_ms) / 1000

        return delta_speed / delta_time