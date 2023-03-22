'''Additional functions for time and date manipulation'''

from datetime import datetime, timedelta, time
from models.exceptions import InvalidDateTimePassedError, InvalidDatePassedError

def is_datetime(datetime_str: str) -> bool:
    '''Return whether the string can be interpreted as a datetime'''
    try:
        datetime.strptime(datetime_str, '%d.%m.%Y-%H:%M:%S')
        return True
    except ValueError:
        return False

def try_parse_date(datetime_str: str, last_day=False) -> datetime:
    '''Try parse str to date using pattern dd.mm.yyyy'''
    try:
        datetime_requested = datetime.strptime(datetime_str, '%d.%m.%Y')
        datetime_requested = datetime_requested + timedelta(days=1) if last_day else datetime_requested
        return datetime_requested
    except ValueError:
        raise InvalidDatePassedError

def try_parse_datetime(datetime_str: str, last_day=False) -> datetime:
    '''Try parse str to datetime or date using pattern dd.mm.yyyy-hh:mm:ss or dd.mm.yyyy'''
    try:
        datetime_requested = datetime.strptime(datetime_str, '%d.%m.%Y-%H:%M:%S')
    except ValueError:
        try:
            datetime_requested = try_parse_date(datetime_str, last_day=last_day)
        except InvalidDatePassedError:
            raise InvalidDateTimePassedError
            
    return datetime_requested

def is_datetime_in_interval(datetime_check: datetime, datetime_start: datetime, datetime_end: datetime) -> bool:
    '''Check if specified date fits in the interval'''
    passed_by_start_date = True
    passed_by_end_date = True

    if datetime_start:
        passed_by_start_date = datetime_check >= datetime_start
    if datetime_end:
        passed_by_end_date = datetime_check <= datetime_end

    return (passed_by_start_date and passed_by_end_date)

def get_time(header_datetime: datetime, reading_millis_passed: int) -> time:
    '''Converting milliseconds to real time based on Header's datetime'''
    new_datetime = header_datetime + timedelta(milliseconds=reading_millis_passed)
    new_time = new_datetime.time()
    return new_time
    