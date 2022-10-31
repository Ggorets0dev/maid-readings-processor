#pylint: disable=E0401 E0611 C0301 C0303

import os
import codecs
from loguru import logger
from models.Reading import Reading
from models.Header import Header
from models.exceptions import InvalidLineDetectedError, ReadingWithoutHeaderError, ResourceNotFoundError

class FileParser:
    '''Parsing class of the file with module readings'''

    @staticmethod
    def count_lines(file_path : str) -> int:
        '''Count lines in file'''
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='UTF-8') as file_r:
                return sum(1 for _ in file_r)
        else:
            raise ResourceNotFoundError(file_path)


    @staticmethod
    def validate_readings_by_time(file_path : str, log_success=True) -> bool:
        '''Check whether each next date/time is later than the previous ones'''
        bad_lines_inxs = []
        line_inx = 0
        new_section = False
        last_header = None
        last_reading = None

        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path) 

        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()
                line_inx += 1

                if not line:                    
                    if len(bad_lines_inxs) == 0:
                        if log_success:
                            logger.success(f"File {file_path} was successfully checked, all time and date values increase over time")
                        return True

                    elif len(bad_lines_inxs) != 0:
                        logger.error(f"File {file_path} did not pass the validation, found inconsistencies with the time sequence in line(s) number: {', '.join(bad_lines_inxs)}")
                        return False
                
                else:                    
                    if Header.is_header(line):
                        if (last_header is not None) and (last_header.date > Header(line).date):
                            bad_lines_inxs.append(str(line_inx))
                        last_header = Header(line)
                        new_section = True

                    elif Reading.is_reading(line):
                        if (last_reading is not None) and (last_reading.millis_passed >= Reading(line).millis_passed) and not new_section:
                            bad_lines_inxs.append(str(line_inx))
                        last_reading = Reading(line)
                        new_section = False

    @staticmethod
    def validate_readings_by_pattern(file_path : str, log_success=True) -> bool:
        '''Check if all lines of the file correspond to the Header or Reading patterns'''
        bad_lines_inxs = []
        line_inx = 0
        
        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path)
        
        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()
                line_inx += 1
                
                if not line and len(bad_lines_inxs) == 0:
                    if log_success:
                        logger.success(f"File {file_path} was successfully checked, all lines match either header or reading pattern")
                    return True

                elif not line and len(bad_lines_inxs) != 0:
                    logger.error(f"File {file_path} did not pass the validation, found inconsistencies with the template in line(s) number: {', '.join(bad_lines_inxs)}")
                    return False

                elif line  == '\n' or line  == '':
                    continue

                elif not(Header.is_header(line)) and not(Reading.is_reading(line)):
                    bad_lines_inxs.append(str(line_inx))

    @staticmethod
    def reduce_readings(file_path : str) -> str:
        '''Optimizing the file with readings, deleting unnecessary lines'''
        REDUCED_FILE_NAME = os.path.splitext(file_path)[0] + "_reduced.txt"
        last_header = ""

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
                
                elif line  == '\n' or line  == '':
                    continue

                elif Header.is_header(line):
                    if last_header == "" or last_header != line:
                        file_w.write(line)
                    last_header = line
                
                elif Reading.is_reading(line):
                    file_w.write(line)

        return result_path

    @staticmethod
    def parse_readings(file_path : str, fix=False) -> dict[Header, list[Reading]]:
        '''Reading values from a file and transferring them to a list'''
        headers_readings = {}
        readings = []
        last_header = None
        line_inx = 0

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

                elif line  == '\n' or line  == '':
                    continue

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
                
                elif not fix:
                    raise InvalidLineDetectedError(line_inx)
        
        return headers_readings

    @staticmethod
    def split_file(file_path : str, part_size : int) -> int:
        '''Divide file to parts'''
        new_file_path = os.path.splitext(file_path)[0] + "_part_"
        line_inx = 0
        part_inx = 1
        line = ''

        if not os.path.isfile(file_path):
            raise ResourceNotFoundError(file_path)

        file_w = open(new_file_path + str(part_inx) + '.txt', 'w', encoding='UTF-8')
        with open(file_path, encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()
                if line_inx >= part_size and Header.is_header(line):
                    line_inx = 1
                    part_inx += 1
                    file_w.close()
                    file_w = open(new_file_path + str(part_inx) + '.txt', 'w', encoding='UTF-8')
                    file_w.write(line)
                
                elif not line:
                    break

                else:
                    file_w.write(line)
                    line_inx += 1
            file_w.close()
        
        return part_inx

    @staticmethod
    def is_utf8(file_path : str) -> bool:
        '''Check if file is in UTF-8'''
        try:
            with codecs.open(file_path, encoding='utf-8', errors='strict') as file_r:
                for _ in file_r:
                    pass
            return True
        except (IOError, UnicodeDecodeError):
            return False
