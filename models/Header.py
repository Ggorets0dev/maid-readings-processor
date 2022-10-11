class Header:
    '''Header that is read from the file'''

    def __init__(self, date : str, spokes_cnt : int, wheel_circ : int, save_delay : float) -> None:
        self.date = date
        self.spokes_cnt = spokes_cnt
        self.wheel_circ = wheel_circ
        self.save_delay = save_delay
