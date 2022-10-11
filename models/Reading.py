class Reading:
    '''Reading that is read from the file'''

    def __init__(self, reading : str) -> None:
        reading_parts = reading.split(' ')
        self.millis_passed = int(reading_parts[1])
        self.speed = float(reading_parts[3])
        self.voltage = float(reading_parts[4])
    
    
    @staticmethod
    def is_reading(reading : str) -> bool:
        '''Trying to determine if the string is Reading'''
        reading_parts = reading.split(' ')
        try:
            return reading_parts[1].isdigit() and (isinstance(float(reading_parts[3]), float)) and (isinstance(float(reading_parts[4]), float)) and len(reading_parts) == 5
        except IndexError:
            return False
