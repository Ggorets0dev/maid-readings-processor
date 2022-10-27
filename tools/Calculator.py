# pylint: disable=E0401

from models.Header import Header
from models.CountedReading import CountedReading
from models.Reading import Reading

class Calculator:
    '''Operations with readings got from module'''

    @staticmethod
    def convert_readings(headers_readings : dict[Header, list[Reading]], decimal_places : int) -> dict[Header, list[CountedReading]]:
        '''Convert list of Readings to list of CountedReadings'''
        headers_counted_readings = {}
        counted_readings = []
        for header in headers_readings:
            for i in range(len(headers_readings[header])):
                counted_readings.append(CountedReading(headers_readings[header][i], header, decimal_places))
            headers_counted_readings[header] = counted_readings.copy()
            counted_readings.clear()
        return headers_counted_readings

    @staticmethod
    def find_voltage_interval(headers_readings : dict[Header, list[CountedReading]], minimal_voltage=15) -> dict[str, float]:
        '''Find minimal and maximal voltage in all CountedReadings'''
        interval = { 'min': 1000.0, 'max': 0.0 }
        for header in headers_readings:
            for reading in headers_readings[header]:
                if reading.voltage_v < minimal_voltage:
                    continue
                else:
                    interval['min'] = min(interval['min'], reading.voltage_v)
                    interval['max'] = max(interval['max'], reading.voltage_v)
        
        if interval['min'] == 1000.0: # * Check if it's still initial value
            return None

        return interval

    @staticmethod
    def calculate_acceleration(first_speed_kmh : float, first_time_ms : float, second_speed_kmh : float, second_time_ms : float) -> float:
        '''Calculate acceleration between to speeds (m/s)'''
        delta_speed = (second_speed_kmh - first_speed_kmh) * 1000 / 3600
        delta_time = (second_time_ms - first_time_ms) / 1000

        return delta_speed / delta_time      