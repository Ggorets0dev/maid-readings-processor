class Reading:
    '''Reading that is read from the file'''

    PATTERN = "{R} int[millis_passed] | int[impulse_count] | int[analog_voltage]"
    display_cnt = 1

    def __init__(self, reading : str) -> None:
        reading_parts = reading.split(' ')
        self.millis_passed = int(reading_parts[1])
        self.impulse_cnt = int(reading_parts[3])
        self.analog_voltage = int(reading_parts[5].replace('\n', ''))
   
    def display(self, raw=False, to_enumerate=False) -> None:
        '''Displaying Reading in different modes'''
        reading = f"{Reading.display_cnt}) " if to_enumerate else ""
        
        if not raw:
            reading += f"millis_passed: {self.millis_passed} ms, impulse_cnt: {self.impulse_cnt}, analog_voltage: {self.analog_voltage}"
        else:
            reading += f"{self.millis_passed} | {self.impulse_cnt} | {self.analog_voltage}"

        Reading.display_cnt += 1
        print(reading)

    @classmethod
    def create_empty(cls):
        '''Creating an empty instance of a class'''
        reading = cls("{R} " + f"{0} | {0} | {0}")
        return reading

    @staticmethod
    def is_reading(reading : str) -> bool:
        '''Trying to determine if the string is Reading'''
        reading_parts = reading.split(' ')
        try:
            return len(reading_parts) == len(Reading.PATTERN.split(' ')) and reading_parts[1].isdigit() and reading_parts[3].isdigit() and reading_parts[5].replace('\n', '').isdigit()
        except IndexError:
            return False