#pylint: disable=E0401

import os
from typing import Dict, List
from loguru import logger
from models.Reading import Reading
from models.Header import Header

class FileParser:
    '''Parsing class of the file with module readings'''

    @staticmethod
    def reduce_readings(file_path : str) -> str:
        '''Optimizing the file with readings, deleting unnecessary lines'''
        
        REDUCED_FILE_NAME = os.path.splitext(file_path)[0] + "_reduced.txt";
        last_header = ""

        if (not(os.path.isfile(file_path))):
            logger.error(f"File {file_path} not found, no further reduction possible")
            return None

        if (len(os.path.dirname(file_path)) == 0):
            result_path = REDUCED_FILE_NAME
        else:
            result_path = os.path.join(os.path.dirname(file_path), REDUCED_FILE_NAME)

        with open(file_path, 'r', encoding='UTF-8') as file_r, open(result_path, 'w', encoding='UTF-8') as file_w:
            while True:
                line = file_r.readline()

                if not line:
                    break
                
                elif line[1] == "H":
                    if last_header == "" or last_header != line:
                        file_w.write(line)
                    last_header = line
                
                else:
                    file_w.write(line)

        logger.info(f"File {file_path} has been optimized and shortened, the result: {result_path}")
        return result_path


    @staticmethod
    def parse_readings(file_path : str) -> Dict[Header, List[Reading]]:
        '''Reading values from a file and transferring them to a list'''
        
        reduced_path = FileParser.reduce_readings(file_path)

        if reduced_path is None:
            logger.error(f"File {file_path} not found, no further parsing possible")
            return None

        dates_readings = {}
        readings = []
        last_header = None

        with open(reduced_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()

                if not line:
                    if len(readings) != 0:
                        dates_readings[last_header] = readings
                    break

                elif Reading.is_reading(line):
                    readings.append(Reading(line))

                elif Header.is_header(line):
                    if (last_header is not None):
                        dates_readings[last_header] = readings
                        readings.clear()
                    last_header = Header(line)
        
        logger.info(f"File {file_path} was processed, the headers and readings were saved in memory")
        return dates_readings



