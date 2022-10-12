#pylint: disable=C0303 E0401

from argparse import _SubParsersAction, Namespace
from loguru import logger
from tools.FileParser import FileParser
from models.Header import Header
from models.Reading import Reading

class ShowSubParser:
    '''Handling Show method arguments'''

    @staticmethod
    def add_subparser(subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        show_subparser = subparsers.add_parser('show', description='Displaying values on the screen without calculating any information')
        show_subparser.add_argument('-i', '--input', nargs=1, required=True, help='Path to the file with readings')
        show_subparser.add_argument('-he', '--headers', action='store_true', help='Display target: headers')
        show_subparser.add_argument('-re', '--readings', action='store_true', help='Display target: readings')
        show_subparser.add_argument('-r', '--raw', action='store_true', help='Display values without visual processing')
        show_subparser.add_argument('-e', '--enumerate', action='store_true', help='Number displayed values')
        show_subparser.add_argument('-f', '--first', nargs=1, type=int, help='Display first FIRST values')
        show_subparser.add_argument('-l', '--last', nargs=1, type=int, help='Display last LAST values')
        return subparsers

    @staticmethod
    def run_show(namespace : Namespace) -> None:
        '''Run if show subparser was called'''
        file_path = namespace.input[0]
        Header.display_cnt = 1
        Reading.display_cnt = 1

        if namespace.headers or namespace.readings:
            headers_readings = FileParser.parse_readings(file_path)

            if namespace.first or namespace.last:
                if namespace.first and namespace.headers:
                    Header.display_list(headers=list(headers_readings.keys())[:namespace.first[0]], raw=namespace.raw, to_enumerate=namespace.enumerate)

                elif namespace.last and namespace.headers:
                    Header.display_list(headers=list(headers_readings.keys())[len(list(headers_readings.keys())) - namespace.last[0]:], raw=namespace.raw, to_enumerate=namespace.enumerate)
                
                elif namespace.first and namespace.readings:
                    display_cnt = 0
                    reading_inx = 0
                    readings_inx = 0
                    readings = headers_readings[list(headers_readings.keys())[readings_inx]]
                    
                    while True:
                        if reading_inx >= len(readings):
                            reading_inx = 0
                            readings_inx += 1
                            readings = headers_readings[list(headers_readings.keys())[readings_inx]]
                        
                        elif display_cnt == namespace.first[0]:
                            break
                        
                        else:
                            readings[reading_inx].display(raw=namespace.raw)
                            reading_inx += 1
                            display_cnt += 1
                        

                elif namespace.last and namespace.readings:
                    display_cnt = 0
                    readings_passed_cnt = 0
                    reading_inx = 0
                    readings_inx = -1
                    readings = headers_readings[list(headers_readings.keys())[readings_inx]]

                    while True:
                        if readings_passed_cnt + len(readings) >= namespace.last[0]:
                            Reading.display_list(readings=readings[len(readings)-namespace.last[0]+readings_passed_cnt:], raw=namespace.raw, to_enumerate=namespace.enumerate)
                            display_cnt += len(readings[len(readings)-namespace.last[0]+readings_passed_cnt:])
                            
                            while display_cnt < namespace.last[0]:
                                readings_inx += 1
                                readings = headers_readings[list(headers_readings.keys())[readings_inx]]
                                Reading.display_list(readings=readings, raw=namespace.raw, to_enumerate=namespace.enumerate)
                                display_cnt += len(readings)

                            break
                        
                        else:
                            readings_passed_cnt += len(readings)
                            readings_inx -= 1
                            readings = headers_readings[list(headers_readings.keys())[readings_inx]]

            
            else:
                if namespace.headers:
                    for header in headers_readings:
                        header.display(raw=namespace.raw, to_enumerate=namespace.enumerate)
                    
                elif namespace.readings:
                    for header in headers_readings:
                        for reading in headers_readings[header]:
                            reading.display(raw=namespace.raw, to_enumerate=namespace.enumerate)

            


        else:
            logger.error("Display target not selected (--headers or --readings)")