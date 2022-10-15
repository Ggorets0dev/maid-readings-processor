from typing import List
from datetime import date
from dateutil.parser import parse

class Header:
    '''Header that is read from the file'''

    display_cnt = 1
    PATTERN = "{H} str[date] ( int[spokes_count] | int[wheel_circumference] | float[save_delay] | int[smaller_resistor] | int[bigger_resistor] )"

    def __init__(self, header : str) -> None:
        header_parts = header.split(' ')
        date_parts = header_parts[1].split('.')
        
        self.date = date(int(date_parts[2]), int(date_parts[1]), int(date_parts[0]))
        self.spokes_cnt = int(header_parts[3])
        self.wheel_circ = int(header_parts[5])
        self.save_delay = float(header_parts[7])
        self.volt_divider_small = int(header_parts[9])
        self.volt_divider_big = int(header_parts[11])

    def display(self, raw : bool, to_enumerate : bool) -> None:
        '''Displaying Header in different modes'''
        header = ""

        if to_enumerate:
            header += f"{Header.display_cnt}) "
        
        if not raw:
            header += f"date: {self.date} | config: [spokes count: {self.spokes_cnt}, wheel circumfulence: {self.wheel_circ}, save delay: {self.save_delay}, R1 divider: {self.volt_divider_small}, R2 divider: {self.volt_divider_big}]"
        else:
            header += f"{self.date} ({self.spokes_cnt} {self.wheel_circ} {self.save_delay} {self.volt_divider_small} {self.volt_divider_big})"
       
        Header.display_cnt += 1
        print(header)

    @staticmethod
    def display_list(headers : List, raw : bool, to_enumerate : bool) -> None:
        '''Display amount of Headers'''
        for header in headers:
            header.display(raw=raw, to_enumerate=to_enumerate)

    @staticmethod
    def is_date(date_str : str, fuzzy=False) -> bool:
        '''Return whether the string can be interpreted as a date'''
        try:
            parse(date_str, fuzzy=fuzzy)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_header(header : str) -> bool:
        '''Trying to determine if the string is Header'''
        header_parts = header.split(' ')
        try:
            return len(header_parts) == len(Header.PATTERN.split(' ')) and Header.is_date(header_parts[1]) and header_parts[3].isdigit() and header_parts[5].isdigit() and (isinstance(float(header_parts[7]), float)) and header_parts[9].isdigit() and header_parts[11].isdigit()
        except IndexError:
            return False
