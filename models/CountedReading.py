#pylint: disable=C0301 E0401 E0611

from models.Reading import Reading

class CountedReading:
    '''CountedReading that is read from the file'''

    display_cnt = 1
    PATTERN = "{R} time[time] | int[millis_passed] | float[speed_kmh] | float[voltage_v]"

    def __init__(self, reading : Reading, spokes_cnt : int, wheel_circ : int, max_voltage : int, save_delay : float) -> None:
        self.time = None
        self.millis_passed = reading.millis_passed
        self.speed_kmh = CountedReading.calculate_speed(impulse_cnt=reading.impulse_cnt, spokes_cnt=spokes_cnt, wheel_circ=wheel_circ, save_delay=save_delay)
        self.voltage_v = CountedReading.calculate_voltage(analog_voltage=reading.analog_voltage, max_voltage=max_voltage)

    def display(self, raw=False, to_enumerate=False, decimal_places=2) -> None:
        '''Displaying CountedReading in different modes'''
        reading = f"{CountedReading.display_cnt}) " if to_enumerate else ""

        if not raw:
            reading += f"time: {self.time.strftime('%H:%M:%S:%f')}, millis_passed: {self.millis_passed}, speed_kmh: {round(self.speed_kmh, decimal_places)} km/h, voltage_v: {round(self.voltage_v, decimal_places)} v"
        else:
            reading += f"{self.time} | {self.millis_passed} | {round(self.speed_kmh, decimal_places)} | {round(self.voltage_v, decimal_places)}"

        CountedReading.display_cnt += 1
        print(reading)

    @staticmethod
    def display_list(readings : list, raw=False, to_enumerate=False, decimal_places=2) -> None:
        '''Display amount of CountedReadings'''
        for reading in readings:
            reading.display(raw=raw, to_enumerate=to_enumerate, decimal_places=decimal_places)

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
