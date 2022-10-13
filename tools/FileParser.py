#pylint: disable=E0401 C0301 C0303

import os
from typing import Dict, List
from loguru import logger
from models.Reading import Reading
from models.Header import Header

class FileParser:
    '''Parsing class of the file with module readings'''

    @staticmethod
    def validate_readings_by_time(file_path : str) -> bool:
        '''Check whether each next date/time is later than the previous ones'''
        bad_lines_inxs = []
        line_inx = 0
        last_header = None
        last_reading = None

        if not os.path.isfile(file_path):
            logger.error(f"File {file_path} not found, no further validation possible")
            return False   

        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()
                line_inx += 1

                if not line and len(bad_lines_inxs) == 0:
                    logger.success(f"File {file_path} was successfully checked, all time and date values increase over time")
                    return True

                elif not line and len(bad_lines_inxs) != 0:
                    logger.error(f"File {file_path} did not pass the validation, found inconsistencies with the time sequence in line(s) number: {', '.join(bad_lines_inxs)}")
                    return False
                
                elif Header.is_header(line):
                    if (last_header is not None) and (last_header.date > Header(line).date):
                        bad_lines_inxs.append(str(line_inx))
                    last_header = Header(line)
                    last_reading = None

                elif Reading.is_reading(line):
                    if (last_reading is not None) and (last_reading.millis_passed >= Reading(line).millis_passed):
                        bad_lines_inxs.append(str(line_inx))
                    last_reading = Reading(line)

    @staticmethod
    def validate_readings_by_pattern(file_path : str) -> bool:
        '''Check if all lines of the file correspond to the Header or Reading patterns'''
        bad_lines_inxs = []
        line_inx = 0
        
        if not os.path.isfile(file_path):
            logger.error(f"File {file_path} not found, no further validation possible")
            return False
        
        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()
                line_inx += 1
                
                if not line and len(bad_lines_inxs) == 0:
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
            logger.error(f"File {file_path} not found, no further reduction possible")
            return None

        elif not FileParser.validate_readings_by_pattern(file_path) or not FileParser.validate_readings_by_time(file_path):
            logger.error("Specified file does not match the pattern or time, no futher reduction is possible")
            return None

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

                elif line[1] == "H":
                    if last_header == "" or last_header != line:
                        file_w.write(line)
                    last_header = line
                
                else:
                    file_w.write(line)

        return result_path


    @staticmethod
    def parse_readings(file_path : str) -> Dict[Header, List[Reading]]:
        '''Reading values from a file and transferring them to a list'''
        
        reduced_path = FileParser.reduce_readings(file_path)

        if reduced_path is None:
            logger.error("Failed to retrieve values from file because previous operations were not successful")
            return None

        headers_readings = {}
        readings = []
        last_header = None

        with open(reduced_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()

                if not line:
                    if len(readings) != 0:
                        headers_readings[last_header] = readings
                    break

                elif line  == '\n' or line  == '':
                    continue

                elif Reading.is_reading(line):
                    readings.append(Reading(line))

                elif Header.is_header(line):
                    if (last_header is not None):
                        headers_readings[last_header] = readings.copy()
                        readings.clear()
                    last_header = Header(line)
        
        return headers_readings