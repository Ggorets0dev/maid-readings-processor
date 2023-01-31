'''ReadableFile location'''

import os
import time
from loguru import logger
from models.exceptions import ResourceSizeExceededError, ResourceNotFoundError, ResourceWrongEncodingError, InvalidResourceError
from tools.FileParser import FileParser
class ReadableFile:
    '''File which can be handled by functions'''
    MAXIMAL_FILE_LENGTH = 10_500_000
    VISIBLE_FILE_LENGTH = MAXIMAL_FILE_LENGTH / 5

    def __init__(self, file_path : str) -> None:
        if os.path.isfile(file_path):
            lines_cnt = FileParser.count_lines(file_path)
            if lines_cnt < ReadableFile.MAXIMAL_FILE_LENGTH:
                
                # NOTE - Large file size time warning
                if lines_cnt > ReadableFile.VISIBLE_FILE_LENGTH:
                    start_time = time.time()
                    logger.warning(f"Specified file has a large size in the form of {lines_cnt} line, the check may take some time")

                if FileParser.is_utf8(file_path):
                    if FileParser.validate_readings_by_pattern(file_path=file_path, log_success=False) and FileParser.validate_readings_by_time(file_path=file_path, log_success=False):
                        self.name = file_path

                        if lines_cnt > ReadableFile.VISIBLE_FILE_LENGTH:
                            logger.success(f"Verification of the file successfully completed, time spent: {round(time.time() - start_time, 3)} seconds")
                    else:
                        raise InvalidResourceError(file_path)
                else:
                    raise ResourceWrongEncodingError(file_path)
            else:
                raise ResourceSizeExceededError(file_path, lines_cnt, ReadableFile.MAXIMAL_FILE_LENGTH)
        else:
            raise ResourceNotFoundError(file_path)