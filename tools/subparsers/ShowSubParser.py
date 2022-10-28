#pylint: disable=C0301 C0303 E0401 E0611

from datetime import date
from argparse import _SubParsersAction, Namespace
from loguru import logger
from tools.FileParser import FileParser
from tools.Calculator import Calculator
from models.Header import Header
from models.Reading import Reading
from models.ReadableFile import ReadableFile
from models.CountedReading import CountedReading

class ShowSubParser:
    '''Output files or other data'''

    @staticmethod
    def add_subparser(subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        show_subparser = subparsers.add_parser('show', description='Displaying values on the screen without calculating any information')
        show_subparser.add_argument('-i', '--input', nargs=1, type=ReadableFile, required=True, help='Path to the file with readings')
        
        # NOTE - One of this targets must be specified
        show_subparser.add_argument('-he', '--header', action='store_true', help='Display target: headers')
        show_subparser.add_argument('-re', '--reading', action='store_true', help='Display target: readings')
        show_subparser.add_argument('-da', '--date', nargs=1, help='Display target: values written in specified day (dd.mm.yyyy)')
        show_subparser.add_argument('-lc', '--line-count', action='store_true', help='Display number of lines in file')

        # NOTE - Modes of visualisation
        show_subparser.add_argument('--fix', action='store_true', help='Try to fix the file automatically')
        show_subparser.add_argument('-r', '--raw', action='store_true', help='Display values without visual processing')
        show_subparser.add_argument('-e', '--enumerate', action='store_true', help='Number displayed values')
        show_subparser.add_argument('-f', '--first', nargs=1, type=int, help='Display first FIRST values')
        show_subparser.add_argument('-l', '--last', nargs=1, type=int, help='Display last LAST values')
        show_subparser.add_argument('-o', '--original', action='store_true', help='No line check and no file shortening (enabled by default)')
        show_subparser.add_argument('-c', '--calculate', nargs=1, type=int, help='Verify the number of pulses in km/h and the analog value in volts with CALCULATE decimal places (disabled by default)')
        return subparsers

    @staticmethod
    def run_show(namespace : Namespace) -> None:
        '''Run if Show subparser was called'''
        file_path = namespace.input[0].name

        # NOTE - Processing targets: --line-count
        if namespace.line_count:
            print(f"Lines in requested file: {FileParser.count_lines(file_path=file_path)}")
            return

        # NOTE - Loading the readings file
        headers_readings = FileParser.parse_readings(file_path=file_path, check=not(namespace.original), fix=namespace.fix)
        if headers_readings is None:
            logger.error("Failed to display values because past operations have not been completed")
            return
        
        elif namespace.calculate:
            if namespace.calculate[0] <= 5 and namespace.calculate[0] > 0:
                headers_readings = Calculator.convert_readings(headers_readings, namespace.calculate[0])
            else:
                logger.error("Calculation accuracy --calculate: maximal: 5, minimal: 1 (decimal places)")
                return

        # SECTION - Processing targets: --header --reading --date
        if namespace.header or namespace.reading:
            if namespace.first or namespace.last:
                if namespace.first and namespace.header:
                    Header.display_list(headers=list(headers_readings.keys())[:namespace.first[0]], raw=namespace.raw, to_enumerate=namespace.enumerate)

                elif namespace.last and namespace.header:
                    Header.display_list(headers=list(headers_readings.keys())[len(list(headers_readings.keys())) - namespace.last[0]:], raw=namespace.raw, to_enumerate=namespace.enumerate)
                
                elif namespace.first and namespace.reading:
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
                            readings[reading_inx].display(raw=namespace.raw, to_enumerate=namespace.enumerate)
                            reading_inx += 1
                            display_cnt += 1
                        

                elif namespace.last and namespace.reading:
                    display_cnt = 0
                    readings_passed_cnt = 0
                    reading_inx = 0
                    readings_inx = -1
                    readings = headers_readings[list(headers_readings.keys())[readings_inx]]

                    while True:
                        if readings_passed_cnt + len(readings) >= namespace.last[0]:
                            if isinstance(readings[0], Reading):
                                Reading.display_list(readings=readings[len(readings)-namespace.last[0]+readings_passed_cnt:], raw=namespace.raw, to_enumerate=namespace.enumerate)
                            elif isinstance(readings[0], CountedReading):
                                CountedReading.display_list(readings=readings[len(readings)-namespace.last[0]+readings_passed_cnt:], raw=namespace.raw, to_enumerate=namespace.enumerate)
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
                if namespace.header:
                    for header in headers_readings:
                        header.display(raw=namespace.raw, to_enumerate=namespace.enumerate)
                    
                elif namespace.reading:
                    for header in headers_readings:
                        for reading in headers_readings[header]:
                            reading.display(raw=namespace.raw, to_enumerate=namespace.enumerate)

            
        elif namespace.date:
            try:
                date_parts = namespace.date[0].split('.')
                date_requested = date(int(date_parts[2]), int(date_parts[1]), int(date_parts[0]))
            except (IndexError, ValueError):
                logger.error("Failed to parse the specified date (expected pattern: dd.mm.yyyy)")
                return

            for header in headers_readings:
                if header.date == date_requested:
                    if isinstance(headers_readings[header][0], Reading):
                        Reading.display_list(headers_readings[header], raw=namespace.raw, to_enumerate=namespace.enumerate)
                    elif isinstance(headers_readings[header][0], CountedReading):
                        CountedReading.display_list(headers_readings[header], raw=namespace.raw, to_enumerate=namespace.enumerate)
                    return
            logger.info("No readings for requested date were found")
            return

        else:
            logger.error("Display target not selected (--header / --reading / --date)")
            return
        # !SECTION