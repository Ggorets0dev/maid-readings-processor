from typing import List

class Header:
    '''Header that is read from the file'''

    def __init__(self, header : str) -> None:
        header_parts = header.split(' ')
        self.date = header_parts[1]
        self.spokes_cnt = int(header_parts[3])
        self.wheel_circ = int(header_parts[5])
        self.save_delay = float(header_parts[7])

    def display(self, raw : bool) -> None:
        '''Displaying Header in different modes'''
        if not raw:
            print(f"date: {self.date} | config: [spokes count: {self.spokes_cnt}, wheel circumfulence: {self.wheel_circ}, save delay: {self.save_delay}]")
        else:
            print(f"{self.date} ({self.spokes_cnt} {self.wheel_circ} {self.save_delay})")

    @staticmethod
    def display_list(headers : List, raw : bool) -> None:
        '''Display amount of Headers'''
        for header in headers:
            header.display(raw=raw)

    @staticmethod
    def is_header(header : str) -> bool:
        '''Trying to determine if the string is Header'''
        header_parts = header.split(' ')
        try:
            return header_parts[3].isdigit() and header_parts[5].isdigit() and (isinstance(float(header_parts[7]), float)) and len(header_parts) == 9
        except IndexError:
            return False
