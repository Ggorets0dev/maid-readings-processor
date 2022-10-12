from typing import List

class Reading:
    '''Reading that is read from the file'''

    display_cnt = 1

    def __init__(self, reading : str) -> None:
        reading_parts = reading.split(' ')
        self.millis_passed = int(reading_parts[1])
        self.speed = float(reading_parts[3])
        self.voltage = float(reading_parts[4])
   
    def display(self, raw : bool, to_enumerate : bool) -> None:
        '''Displaying Reading in different modes'''
        reading = ""

        if to_enumerate:
            reading += f"{Reading.display_cnt}) "
        
        if not raw:
            reading += f"millis_passed: {self.millis_passed} | speed: {self.speed} | voltage: {self.voltage}"
        else:
            reading += f"{self.millis_passed} | {self.speed} | {self.voltage}"

        Reading.display_cnt += 1
        print(reading)

    @staticmethod
    def display_list(readings : List, raw : bool, to_enumerate : bool) -> None:
        '''Display amount of Readings'''
        for reading in readings:
            reading.display(raw=raw, to_enumerate=to_enumerate)

    @staticmethod
    def is_reading(reading : str) -> bool:
        '''Trying to determine if the string is Reading'''
        reading_parts = reading.split(' ')
        try:
            return reading_parts[1].isdigit() and (isinstance(float(reading_parts[3]), float)) and (isinstance(float(reading_parts[4]), float)) and len(reading_parts) == 5
        except IndexError:
            return False
