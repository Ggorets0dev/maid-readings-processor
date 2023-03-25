'''FileParser location'''

import os
import codecs
from copy import copy
from datetime import datetime, timedelta
from typing import Dict, List
import yaml
from loguru import logger
from tools.additional_datetime_utils import is_datetime_in_interval
from models.reading import Reading
from models.header import Header
from models.counted_reading import CountedReading
from models.config import Config
from models.exceptions import ReadingWithoutHeaderError, ResourceNotFoundError

class FileParser:
    '''Manipulation of files that do not perform calculations'''

    @staticmethod
    def show_headers(file_path: str, datetime_start: datetime, datetime_end: datetime, raw=False, to_enumerate=False) -> None:
        '''Display all headers (ignore duplicates by date)'''
        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path) 

        found_any = False
        last_header = Header.create_empty()
        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()

                if not line:
                    break

                elif Header.is_header(line):
                    header = Header(line)
                    if is_datetime_in_interval(header.datetime, datetime_start, datetime_end) and header.datetime.date != last_header.datetime.date:
                        header.display(raw=raw, to_enumerate=to_enumerate)
                        last_header = header
                        found_any = True
            
            if not found_any:
                logger.info('No headers was found on specified datetime')
    
    @staticmethod
    def show_readings(file_path: str, datetime_start: datetime, datetime_end: datetime, config: Config, calculated=False, raw=False, to_enumerate=False) -> None:
        '''Display all readings (raw or calculated)'''
        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path)
        
        found_any = False
        last_header = None
        with open(file_path, 'r', encoding='UTF-8') as file_r: 
            while True:
                line = file_r.readline()

                if not line:
                    break
                
                elif Header.is_header(line):
                    last_header = Header(line)

                elif Reading.is_reading(line) and last_header:
                    found_any = True
                    reading = Reading(line)
                    reading_datetime = last_header.datetime + timedelta(milliseconds=reading.millis_passed)
                    
                    if reading_datetime > datetime_end:
                        break

                    elif reading_datetime < datetime_start:
                        continue

                    if calculated:
                        reading = CountedReading(reading, last_header.spokes_cnt, last_header.wheel_circ, last_header.max_voltage, last_header.save_delay)
                        reading.time = reading_datetime.time()
                        reading.display(normal_speed_interval=config.normal_speed_interval, normal_voltage_interval=config.normal_voltage_interval, raw=raw, to_enumerate=to_enumerate, decimal_places=3)
                    else:
                        reading.display(raw=raw, to_enumerate=to_enumerate)

            if not found_any:
                logger.info('No readings was found on specified datetime')

    @staticmethod
    def count_lines(file_path: str) -> int:
        '''Count lines in file'''
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='UTF-8') as file_r:
                return sum(1 for _ in file_r)
        else:
            raise ResourceNotFoundError(file_path)

    @staticmethod
    def validate_readings_by_time(file_path: str, log_success=True) -> bool:
        '''Check whether each next date/time is later than the previous ones'''
        bad_lines_inxs = []
        line_inx = 0
        new_section = False
        last_header = last_reading = None

        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path) 

        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()
                line_inx += 1

                if not line:                    
                    if len(bad_lines_inxs) == 0:
                        if log_success:
                            logger.success(f"File {file_path} passed the time sequence check")
                        return True

                    elif len(bad_lines_inxs) != 0:
                        logger.error(f"File {file_path} did not pass the validation, found inconsistencies with the time sequence in line(s) number: {', '.join(bad_lines_inxs)}")
                        return False
                
                else:                    
                    if Header.is_header(line):
                        if (last_header is not None) and (last_header.datetime > Header(line).datetime):
                            bad_lines_inxs.append(str(line_inx))
                        last_header = Header(line)
                        new_section = True

                    elif Reading.is_reading(line):
                        if (last_reading is not None) and (last_reading.millis_passed > Reading(line).millis_passed) and not new_section:
                            bad_lines_inxs.append(str(line_inx))
                        last_reading = Reading(line)
                        new_section = False

    @staticmethod
    def validate_readings_by_pattern(file_path: str, log_success=True) -> bool:
        '''Check if all lines of the file correspond to the Header or Reading patterns'''
        bad_lines_inxs = []
        line_inx = 0
        last_header = None

        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path)
        
        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()
                line_inx += 1
                
                if not line and len(bad_lines_inxs) == 0:
                    if log_success:
                        logger.success(f"File {file_path} passed the pattern check")
                    return True

                elif not line and len(bad_lines_inxs) != 0:
                    logger.error(f"File {file_path} did not pass the validation, found inconsistencies with the template in line(s) number: {', '.join(bad_lines_inxs)}")
                    return False

                elif line  == '\n' or line  == '':
                    continue

                elif Header.is_header(line):
                    last_header = Header(line)

                elif (not(Header.is_header(line)) and not(Reading.is_reading(line))) or (Reading.is_reading(line) and not last_header):
                    bad_lines_inxs.append(str(line_inx))

    @staticmethod
    def reduce_readings(file_path: str) -> str:
        '''Optimizing the file with readings, deleting unnecessary lines'''
        REDUCED_FILE_NAME = os.path.splitext(file_path)[0] + "_reduced.txt"
        last_header = None

        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path)

        if len(os.path.dirname(file_path)) == 0:
            result_path = REDUCED_FILE_NAME
        else:
            result_path = os.path.join(os.path.dirname(file_path), REDUCED_FILE_NAME)

        with open(file_path, 'r', encoding='UTF-8') as file_r, open(result_path, 'w', encoding='UTF-8') as file_w:
            while True:
                line = file_r.readline()

                if not line:
                    break

                elif Header.is_header(line):
                    if not last_header or (last_header and last_header.datetime != Header(line).datetime):
                        file_w.write(line)
                    last_header = Header(line)
                
                elif Reading.is_reading(line):
                    file_w.write(line)

        return result_path

    @staticmethod
    def parse_readings(file_path: str) -> Dict[Header, List[Reading]]:
        '''Reading values from a file and transferring them to a list'''
        headers_readings = {}
        readings = []
        line_inx = 0
        last_header = None

        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path)

        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()
                line_inx += 1

                if not line:
                    if len(readings) != 0:
                        headers_readings[last_header] = readings
                    break

                elif Reading.is_reading(line):
                    if last_header is not None:
                        readings.append(Reading(line))
                    else:
                        raise ReadingWithoutHeaderError(line_inx)

                elif Header.is_header(line):
                    if (last_header is not None):
                        headers_readings[last_header] = readings.copy()
                        readings.clear()
                    last_header = Header(line)
        
        return headers_readings

    @staticmethod
    def split_file(file_path: str, part_size: int) -> int:
        '''Divide file to parts'''
        new_file_path = os.path.splitext(file_path)[0] + "_part_"
        line_inx, part_inx = 0, 1

        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path)

        file_w = open(new_file_path + str(part_inx) + '.txt', 'w', encoding='UTF-8')
        last_header = current_header = None

        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()

                if not line:
                    break

                if Header.is_header(line):
                    current_header = Header(line)

                    if line_inx >= part_size and (not last_header or (last_header and Header(line).datetime.date() != last_header.datetime.date())):
                        line_inx = 1
                        part_inx += 1
                        file_w.close()
                        file_w = open(f"{new_file_path}{part_inx}.txt", 'w', encoding='UTF-8')
                    
                    file_w.write(line)
                    line_inx += 1
                    last_header = copy(current_header)

                elif Reading.is_reading(line):
                    file_w.write(line)
                    line_inx += 1
            
            file_w.close()
        
        return part_inx

    @staticmethod
    def is_utf8(file_path: str) -> bool:
        '''Check if file is in UTF-8'''
        try:
            with codecs.open(file_path, encoding='UTF-8', errors='strict') as file_r:
                for _ in file_r:
                    pass
            return True
        except (IOError, UnicodeDecodeError):
            return False

    @staticmethod
    def parse_aliases(file_path: str) -> Dict:
        '''Collecting aliases for commands'''
        if not os.path.isfile(file_path):
            return { 'exists': False, 'data': [] }
        
        with open(file_path, 'r', encoding='UTF-8') as file_read:
            aliases = yaml.safe_load(file_read)

        try:
            return { 'exists': True, 'data': aliases['aliases'] }
        except KeyError:
            return { 'exists': True, 'data': [] }
    
    @staticmethod
    def save_aliases(file_path: str, aliases: List[Dict[str, str]]) -> bool:
        '''Adding new alias for command'''
        aliases = { 'aliases': aliases }
        with open(file_path, 'w', encoding='UTF-8') as file_write:
            yaml.dump(aliases, file_write, default_flow_style=False)    