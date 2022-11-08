# pylint: disable=E0401 E0611

import os
from models.exceptions import ResourceSizeExceededError, ResourceNotFoundError, ResourceWrongEncodingError, InvalidResourceError
from tools.FileParser import FileParser

class ReadableFile:
    '''File which can be handled by functions'''

    MAXIMAL_FILE_LENGTH = 10_500_000

    def __init__(self, file_path : str) -> None:
        if os.path.isfile(file_path):
            lines_cnt = FileParser.count_lines(file_path)
            if lines_cnt < ReadableFile.MAXIMAL_FILE_LENGTH:
                if FileParser.is_utf8(file_path):
                    if FileParser.validate_readings_by_pattern(file_path=file_path, log_success=False) and FileParser.validate_readings_by_time(file_path=file_path, log_success=False):
                        self.name = file_path
                    else:
                        raise InvalidResourceError(file_path)
                else:
                    raise ResourceWrongEncodingError(file_path)
            else:
                raise ResourceSizeExceededError(file_path, lines_cnt, ReadableFile.MAXIMAL_FILE_LENGTH)
        else:
            raise ResourceNotFoundError(file_path)