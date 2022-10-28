# pylint: disable=E0401 E0611

import os
from models.exceptions import ResourceSizeExceededError, ResourceNotFoundError, ResourceWrongEncodingError
from tools.FileParser import FileParser

class ReadableFile:
    '''File which can be handled by functions'''

    MAXIMAL_FILE_LENGTH = 10_500_000

    def __init__(self, file_path : str) -> None:
        if os.path.isfile(file_path):
            lines_cnt = FileParser.count_lines(file_path)
            if lines_cnt < ReadableFile.MAXIMAL_FILE_LENGTH:
                if FileParser.is_utf8(file_path):
                    self.name = file_path
                else:
                    raise ResourceWrongEncodingError(file_path)
            else:
                raise ResourceSizeExceededError(file_path, lines_cnt, ReadableFile.MAXIMAL_FILE_LENGTH)
        else:
            raise ResourceNotFoundError(file_path)