#pylint: disable=E0401 E0611 W0707 C0301

from datetime import datetime
from colorama import Fore, Style
from tools.additional_datetime_utils import is_datetime
from tools.text_formatting_utils import cprint
class Header:
    '''Header that is read from the file'''

    display_cnt = 1
    PATTERN = "{H} datetime[datetime] ( int[spokes_count] | int[wheel_circumference] | float[save_delay] | int[max_voltage] )"

    def __init__(self, header : str) -> None:
        header_parts = header.split(' ')
        self.datetime = datetime.strptime(header_parts[1], '%d.%m.%Y-%H:%M:%S')
        self.spokes_cnt = int(header_parts[3])
        self.wheel_circ = int(header_parts[5])
        self.max_voltage = int(header_parts[7])
        self.save_delay = float(header_parts[9])

    def display(self, raw=False, to_enumerate=False, time=True) -> None:
        '''Displaying Header in different modes'''
        header = f"{Header.display_cnt}) " if to_enumerate else ""
        
        if raw:
            header += f"{self.datetime.strftime('%d.%m.%Y-%H:%M:%S')} ( {self.spokes_cnt} | {self.wheel_circ} | {self.max_voltage} | {self.save_delay} )"
        elif not time:
            header += f"datetime: {self.datetime.strftime('%d.%m.%Y')} | config: [spokes count: {self.spokes_cnt}, wheel circumfulence: {self.wheel_circ}mm, max_voltage: {self.max_voltage}v, save delay: {self.save_delay}s]"
        else:
            header += f"datetime: {self.datetime.strftime('%d.%m.%Y-%H:%M:%S')} | config: [spokes count: {self.spokes_cnt}, wheel circumfulence: {self.wheel_circ}mm, max_voltage: {self.max_voltage}v, save delay: {self.save_delay}s]"
       
        cprint(msg=header, fore=Fore.WHITE, style=Style.BRIGHT)
        Header.display_cnt += 1

    @staticmethod
    def display_list(headers : list, raw=False, to_enumerate=False) -> None:
        '''Display amount of Headers'''
        for header in headers:
            header.display(raw=raw, to_enumerate=to_enumerate)

    @staticmethod
    def is_header(header : str) -> bool:
        '''Trying to determine if the string is Header'''
        header_parts = header.split(' ')
        try:
            return len(header_parts) == len(Header.PATTERN.split(' ')) and is_datetime(header_parts[1]) and header_parts[3].isdigit() and header_parts[5].isdigit() and header_parts[7].isdigit() and (isinstance(float(header_parts[9]), float))
        except IndexError:
            return False
