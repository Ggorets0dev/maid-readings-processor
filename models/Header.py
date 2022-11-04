#pylint: disable=E0401 E0611 W0707

from datetime import datetime
from tools.additional_datetime_utils import is_datetime

class Header:
    '''Header that is read from the file'''

    display_cnt = 1
    PATTERN = "{H} str[date_time] ( int[spokes_count] | int[wheel_circumference] | float[save_delay] | int[max_voltage] )"

    def __init__(self, header : str) -> None:
        header_parts = header.split(' ')
        
        self.datetime = datetime.strptime(header_parts[1], '%d.%m.%Y-%H:%M:%S')
        self.spokes_cnt = int(header_parts[3])
        self.wheel_circ = int(header_parts[5])
        self.max_voltage = int(header_parts[7])
        self.save_delay = float(header_parts[9])

    def display(self, raw : bool, to_enumerate : bool) -> None:
        '''Displaying Header in different modes'''
        header = f"{Header.display_cnt}) " if to_enumerate else ""
        
        if not raw:
            header += f"datetime: {self.datetime.strftime('%d.%m.%Y-%H:%M:%S')} | config: [spokes count: {self.spokes_cnt}, wheel circumfulence: {self.wheel_circ}mm, max_voltage: {self.max_voltage}v, save delay: {self.save_delay}s]"
        else:
            header += f"{self.datetime.strftime('%d.%m.%Y-%H:%M:%S')} ( {self.spokes_cnt} | {self.wheel_circ} | {self.max_voltage} | {self.save_delay} )"
       
        Header.display_cnt += 1
        print(header)

    @staticmethod
    def display_list(headers : list, raw : bool, to_enumerate : bool) -> None:
        '''Display amount of Headers'''
        for header in headers:
            header.display(raw=raw, to_enumerate=to_enumerate)

    @staticmethod
    def is_header(header : str) -> bool:
        '''Trying to determine if the string is Header'''
        header_parts = header.split(' ')
        try:
            return len(header_parts) == len(Header.PATTERN.split(' ')) and is_datetime(header_parts[1], True) and header_parts[3].isdigit() and header_parts[5].isdigit() and header_parts[7].isdigit() and (isinstance(float(header_parts[9]), float))
        except IndexError:
            return False
