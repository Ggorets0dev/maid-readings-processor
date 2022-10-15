#pylint: disable=C0301 E0401

from typing import List
from models.Reading import Reading
from models.Header import Header
from tools.subparsers.CalcSubParser import CalcSubParser

class CountedReading:
    '''CountedReading that is read from the file'''

    display_cnt = 1
    PATTERN = "{R} int[millis_passed] | float[speed_kmh] | float[voltage_v]"

    def __init__(self, reading : Reading, header : Header, decimal_places : int) -> None:
        self.millis_passed = reading.millis_passed
        self.speed_kmh = CalcSubParser.calculate_speed(impulse_cnt=reading.impulse_cnt, config=header, decimal_places=decimal_places)
        self.voltage_v = CalcSubParser.calculate_voltage(analog_voltage=reading.analog_voltage, config=header, decimal_places=decimal_places)
   
    def display(self, raw : bool, to_enumerate : bool) -> None:
        '''Displaying CountedReading in different modes'''
        reading = ""

        if to_enumerate:
            reading += f"{CountedReading.display_cnt}) "
        
        if not raw:
            reading += f"millis_passed: {self.millis_passed}, speed_kmh: {self.speed_kmh} km/h, voltage_v: {self.voltage_v} v"
        else:
            reading += f"{self.millis_passed} | {self.speed_kmh} | {self.voltage_v}"

        CountedReading.display_cnt += 1
        print(reading)

    @staticmethod
    def display_list(readings : List, raw : bool, to_enumerate : bool) -> None:
        '''Display amount of CountedReadings'''
        for reading in readings:
            reading.display(raw=raw, to_enumerate=to_enumerate)

    @staticmethod
    def is_counted_reading(reading : str) -> bool:
        '''Trying to determine if the string is CountedReading'''
        reading_parts = reading.split(' ')
        try:
            return len(reading_parts) == len(CountedReading.PATTERN.split(' ')) and reading_parts[1].isdigit() and (isinstance(float(reading_parts[3]), float)) and (isinstance(float(reading_parts[5]), float))
        except IndexError:
            return False
