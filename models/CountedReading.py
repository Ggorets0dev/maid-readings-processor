#pylint: disable=C0301 E0401

from datetime import time
from models.Reading import Reading

class CountedReading:
    '''CountedReading that is read from the file'''

    display_cnt = 1
    PATTERN = "{R} int[millis_passed] | float[speed_kmh] | float[voltage_v]"

    def __init__(self, reading : Reading, spokes_cnt : int, wheel_circ : int, max_voltage : int, save_delay : float) -> None:
        self.time = None
        self.millis_passed = reading.millis_passed
        self.speed_kmh = CountedReading.calculate_speed(impulse_cnt=reading.impulse_cnt, spokes_cnt=spokes_cnt, wheel_circ=wheel_circ, save_delay=save_delay)
        self.voltage_v = CountedReading.calculate_voltage(analog_voltage=reading.analog_voltage, max_voltage=max_voltage)
   
    def display(self, raw : bool, to_enumerate : bool, decimal_places=2) -> None:
        '''Displaying CountedReading in different modes'''
        reading = f"{CountedReading.display_cnt}) " if to_enumerate else ""

        if not raw:
            reading += f"time: {CountedReading.round_macros_to_millis(self.time)}, millis_passed: {self.millis_passed}, speed_kmh: {round(self.speed_kmh, decimal_places)} km/h, voltage_v: {round(self.voltage_v, decimal_places)} v"
        else:
            reading += f"{CountedReading.round_macros_to_millis(self.time)} | {self.millis_passed} | {round(self.speed_kmh, decimal_places)} | {round(self.voltage_v, decimal_places)}"

        CountedReading.display_cnt += 1
        print(reading)

    @staticmethod
    def display_list(readings : list, raw : bool, to_enumerate : bool, decimal_places=2) -> None:
        '''Display amount of CountedReadings'''
        for reading in readings:
            reading.display(raw=raw, to_enumerate=to_enumerate, decimal_places=decimal_places)

    @staticmethod
    def is_counted_reading(reading : str) -> bool:
        '''Trying to determine if the string is CountedReading'''
        reading_parts = reading.split(' ')
        try:
            return len(reading_parts) == len(CountedReading.PATTERN.split(' ')) and reading_parts[1].isdigit() and (isinstance(float(reading_parts[3]), float)) and (isinstance(float(reading_parts[5]), float))
        except IndexError:
            return False

    @staticmethod
    def calculate_speed(impulse_cnt : int, spokes_cnt : int, wheel_circ : int, save_delay : float) -> float:
        '''Calculation of speed in km/h based on the number of pulses and configuration from the header'''
        if impulse_cnt != 0:
            speed = (impulse_cnt / spokes_cnt * wheel_circ / 1_000_000) * (60 * 60 / save_delay)
            return speed
        else:
            return 0.0

    @staticmethod
    def calculate_voltage(analog_voltage : int, max_voltage : int) -> float:
        '''Conversion of analog value to real volts'''
        vin = analog_voltage * max_voltage / 1023
        if vin >= 5:
            return vin
        else:
            return 0.0

    @staticmethod
    def round_macros_to_millis(time_req : time) -> str:
        '''Return time with macros converted to millis'''
        time_parts = str(time_req).split('.')
        if len(time_parts) == 2:
            millis = int(time_parts[1]) / 1000
            return f"{time_parts[0]}:{int(millis)}"
        else:
            return time_parts[0]
