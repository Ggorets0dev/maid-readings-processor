class Reading:
    '''Reading that is read from the file'''

    def __init__(self, millis_passed : int, speed : float, voltage : float) -> None:
        self.millis_passed = millis_passed
        self.speed = speed
        self.voltage = voltage
