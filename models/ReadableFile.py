# pylint: disable=E0401 E0611

import os
from loguru import logger
from tools.FileParser import FileParser

class ReadableFile:
    '''File which can be handled by functions'''

    MAXIMAL_FILE_LENGTH = 10_500_000

    def __init__(self, file_path : str) -> None:
        if os.path.isfile(file_path):
            line_cnt = FileParser.count_lines(file_path)
            if line_cnt < ReadableFile.MAXIMAL_FILE_LENGTH:
                if FileParser.is_utf8(file_path):
                    self.name = file_path
                else:
                    logger.error(f"File {file_path} has characters incompatible with UTF-8 encoding")
                    raise UnicodeDecodeError
            else:
                logger.error(f"File {file_path} size ({line_cnt} lines) in lines exceeds the allowable size ({ReadableFile.MAXIMAL_FILE_LENGTH} lines), before processing, divide the file with the reduce command")
                raise Exception("FileSizeExceededError")
        else:
            logger.error(f"No such file or directory: {file_path}")
            raise FileNotFoundError