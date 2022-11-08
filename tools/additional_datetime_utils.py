#pylint: disable=E0401 E0611 W0707 C0200

from datetime import datetime, timedelta
from models.exceptions import InvalidDateTimePassedError
from models.CountedReading import CountedReading

def is_datetime(datetime_str : str) -> bool:
    '''Return whether the string can be interpreted as a datetime'''
    try:
        datetime.strptime(datetime_str, '%d.%m.%Y-%H:%M:%S')
        return True
    except ValueError:
        return False

def try_parse_datetime(datetime_str : str) -> datetime:
    '''Try parse str to date using pattern dd.mm.yyyy_HH:MM:ss'''
    try:
        datetime_requested = datetime.strptime(datetime_str, '%d.%m.%Y-%H:%M:%S')
    except ValueError:
        try:
            datetime_requested = datetime.strptime(datetime_str, '%d.%m.%Y')
        except ValueError:
            raise InvalidDateTimePassedError
        else:
            return datetime_requested
    else:
        return datetime_requested

def is_datetime_in_interval(datetime_check : datetime, datetime_start : datetime, datetime_end : datetime) -> bool:
    '''Check if specified date fits in the interval'''
    passed_by_start_date = True
    passed_by_end_date = True

    if datetime_start:
        passed_by_start_date = datetime_check >= datetime_start
    if datetime_end:
        passed_by_end_date = datetime_check <= datetime_end

    return passed_by_start_date and passed_by_end_date

def set_time(header_datetime : datetime, counted_readings : list[CountedReading]) -> list[CountedReading]:
    '''Converting milliseconds to real time based on Header's datetime'''
    date_temp = header_datetime.date()
    for i in range(len(counted_readings)):
        if i == 0:
            counted_readings[i].time = header_datetime.time()
        else:
            millis_delta = counted_readings[i].millis_passed - counted_readings[i-1].millis_passed
            datetime_temp = datetime.combine(date_temp, counted_readings[i-1].time)
            datetime_temp += timedelta(milliseconds=millis_delta)
            counted_readings[i].time = datetime_temp.time()
    return counted_readings