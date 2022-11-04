#pylint: disable=E0401 E0611

'''Module with all custom exceptions'''

import traceback
from loguru import logger

# NOTE - Custom user-friendly exception hook, shorter and clearer output
def user_exception_hook(e_type, value, tr_bck):
    '''Custom exception handler for whole program'''
    trace = traceback.format_tb(tr_bck, limit=1)
    trace = trace[0].split('\n')[0]
    exc = traceback.format_exception_only(e_type, value)[0]
    logger.error(f"Raised: {exc} at {trace}".replace('\n', ''))


# NOTE - Ability to set something common for all errors
class Error(Exception):
    '''Parenting class for all errors'''
    
    # NOTE - Codes (random by now) of all available errors, KEY MUST BE A CLASS NAME
    CODES = {
        'Error': 0,
        'ResourceSizeExceededError': 421,
        'ResourceNotFoundError': 582,
        'ResourceWrongEncodingError': 638,
        'InvalidResourceReductionError': 472,
        'InvalidLineDetectedError': 124,
        'ReadingWithoutHeaderError': 491,
        'CalledAsModuleError': 362,
        'InvalidDateTimePassedError': 461
    }
    
    def __init__(self) -> None:
        super().__init__()
        self.name = type(self).__name__
        self.code = Error.CODES[self.name]
        logger.error(f"Raised {self.name} (code: {self.code})")


class ResourceSizeExceededError(Error):
    '''There are too many lines in the file requested for processing'''
    def __init__(self, file_path : str, lines_cnt : int, max_lines_cnt : int) -> None:
        super().__init__()
        logger.error(f"File {file_path} size ({lines_cnt} lines) in lines exceeds the allowable size ({max_lines_cnt} lines), before processing, divide the file with the reduce command")

class ResourceNotFoundError(Error):
    '''Failed to find the requested file'''
    def __init__(self, file_path : str) -> None:
        super().__init__()
        logger.error(f"No such file or directory: {file_path}")

class ResourceWrongEncodingError(Error):
    '''Requested file has non-UTF-8 characters'''
    def __init__(self, file_path : str) -> None:
        super().__init__()
        logger.error(f"File {file_path} has characters incompatible with UTF-8 encoding")

class InvalidResourceReductionError(Error):
    '''Attempting to shorten a file that failed validation'''
    def __init__(self, file_path : str) -> None:
        super().__init__()
        logger.error(f"File {file_path} did not pass validation, no futher reduction is possible")

class InvalidLineDetectedError(Error):
    '''String does not match any of the available templates'''
    def __init__(self, line_inx : int) -> None:
        super().__init__()
        logger.error(f"Found line that does not fit any available template: {line_inx} line")

class ReadingWithoutHeaderError(Error):
    '''Reading is not attached to any Header'''
    def __init__(self, line_inx : int) -> None:
        super().__init__()
        logger.error(f"Detected reading without header, it is unclear what to bind to: {line_inx} line")

class CalledAsModuleError(Error):
    '''marp.py called as module to another file'''
    def __init__(self) -> None:
        super().__init__()
        logger.error("Marp was called as a module from another file, such use is not available")

class InvalidDateTimePassedError(Error):
    '''Failed to parse string to date with pattern dd.mm.yyyyy / dd.mm.yyyy-hh:mm:ss'''
    def __init__(self) -> None:
        super().__init__()
        logger.error("Transmitted string could not be converted to a date or datetime (requires dd.mm.yyyy or dd.mm.yyyy-hh:mm:ss template)")
