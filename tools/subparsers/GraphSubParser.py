'''GraphSubParser location'''

from argparse import _SubParsersAction, Namespace
from copy import copy
from typing import List
import matplotlib.pyplot as plt
from loguru import logger
from tools.additional_datetime_utils import try_parse_date, is_datetime_in_interval
from tools.Calculator import Calculator
from models.ReadableFile import ReadableFile
from models.Header import Header
from models.Reading import Reading
from models.CountedReading import CountedReading
from models.BarGraphConfig import BarGraphConfig

class GraphSubParser:
    '''Displaying values from a file with graphs'''

    @classmethod
    def add_subparser(cls, subparsers: _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        graph_subparser = subparsers.add_parser('graph', description='Displaying values from a file with bar graphs')
        graph_subparser.add_argument('-i', '--input', nargs=1, type=ReadableFile, required=True, help='Path to the file with readings')
        graph_subparser.add_argument('-tt', '--travel-time', action='store_true', help='Display the travel time by day')
        graph_subparser.add_argument('-td', '--travel-distance', action='store_true', help='Display the travel distance by day')

        # NOTE - Modes of search and visualization
        graph_subparser.add_argument('-d', '--date', nargs=2, type=str, required=True, help='Date to filter values (specify two for the interval) (dd.mm.yyyy)')
        graph_subparser.add_argument('-a', '--accuracy', nargs=1, type=int, help='Number of decimal places of the displayed values (min: 1, max: 5, default: 2)')
        
        cls.SUBPARSER = graph_subparser
        return subparsers

    @classmethod
    def run_graph(cls, namespace: Namespace) -> None:
        '''Run if graph subparser was called'''
        resource_path = namespace.input[0].name
        decimal_places = namespace.accuracy[0] if namespace.accuracy and 1 < namespace.accuracy[0] <= 5 else 2
        datetime_start = try_parse_date(namespace.date[0])
        datetime_end = try_parse_date(namespace.date[1], last_day=True)
        bar_graph_config = BarGraphConfig() 

        if (datetime_end - datetime_start).days > 30:
            logger.error("Difference between the dates should not be more than a month, because otherwise the diagram will be inconvenient to view")
            return

        if namespace.travel_time:
            travel_times, dates = [], []

            travel_time_sec = 0
            current_header = last_header = previous_reading = None
            skip_header = False

            with open(resource_path, 'r', encoding='UTF-8') as file_read:
                while True:
                    line = file_read.readline()

                    if not line:
                        if travel_time_sec != 0:
                            travel_times.append(travel_time_sec)
                            dates.append(current_header.datetime.strftime('%d %b'))
                        break

                    elif Header.is_header(line):
                        last_header = copy(current_header)
                        current_header = Header(line)

                        if travel_time_sec != 0 and current_header.datetime.date() != last_header.datetime.date():
                            travel_times.append(travel_time_sec)
                            dates.append(last_header.datetime.strftime('%d %b'))
                            travel_time_sec = 0

                        skip_header = not is_datetime_in_interval(current_header.datetime, datetime_start, datetime_end)
                        current_reading = previous_reading = None

                    elif Reading.is_reading(line) and not skip_header and current_header:
                        current_reading = CountedReading(Reading(line), current_header.spokes_cnt, current_header.wheel_circ, current_header.max_voltage, current_header.save_delay)

                        if previous_reading:
                            travel_time_sec += (abs(previous_reading.millis_passed - current_reading.millis_passed) / 1000)

                        previous_reading = copy(current_reading)

            if len(travel_times) != 0:
                bar_graph_config.values_x = dates
                bar_graph_config.values_y = travel_times
                bar_graph_config.label_x = 'Day'
                bar_graph_config.label_y = 'Travel time (sec)'
                bar_graph_config.label_fig = "Travel time by day"
            else:
                logger.info("No travel time was found for specified conditions")
                return

        elif namespace.travel_distance:
            travel_distances, dates = [], []

            travel_distance_km = 0
            current_header = last_header = current_reading = previous_reading = None
            skip_header = False

            with open(resource_path, 'r', encoding='UTF-8') as file_read:
                while True:
                    line = file_read.readline()

                    if not line:
                        if travel_distance_km != 0:
                            travel_distances.append(travel_distance_km)
                            dates.append(current_header.datetime.strftime('%d %b'))
                        break

                    elif Header.is_header(line):
                        last_header = copy(current_header)
                        current_header = Header(line)
                        
                        if travel_distance_km != 0 and current_header.datetime.date() != last_header.datetime.date():
                            travel_distances.append(travel_distance_km)
                            dates.append(last_header.datetime.strftime('%d %b'))
                            travel_distance_km = 0

                        skip_header = not is_datetime_in_interval(current_header.datetime, datetime_start, datetime_end)
                        current_reading = previous_reading = None

                    elif Reading.is_reading(line) and not skip_header and current_header:
                        current_reading = CountedReading(Reading(line), current_header.spokes_cnt, current_header.wheel_circ, current_header.max_voltage, current_header.save_delay)

                        if previous_reading:
                            travel_distance_km += Calculator.calculate_travel_distance(current_reading.speed_kmh, current_reading.millis_passed, previous_reading.millis_passed)

                        previous_reading = copy(current_reading)

            if len(travel_distances) != 0:
                bar_graph_config.values_x = dates
                bar_graph_config.values_y = travel_distances
                bar_graph_config.label_x = 'Day'
                bar_graph_config.label_y = 'Travel distance (km)'
                bar_graph_config.label_fig = "Travel distance by day"
            else:
                logger.info("No travel distances were found for specified conditions")
                return

        else:
            logger.error("Display target not selected (--average-acceleration / --travel-distance)")
            cls.SUBPARSER.print_help()
            return
    
        fig, ax = plt.subplots(num=bar_graph_config.label_fig)
        fig.set_figwidth = 100
        fig.set_figheight = 100
        plt.xlabel(bar_graph_config.label_x, weight='bold')
        plt.ylabel(bar_graph_config.label_y, weight='bold')
        ax.bar(bar_graph_config.values_x, bar_graph_config.values_y)
        ax.set_facecolor('seashell')
        fig.set_facecolor('floralwhite')
        GraphSubParser.draw_values(bar_graph_config.values_x, bar_graph_config.values_y, decimal_places)
        plt.show()

    @staticmethod
    def draw_values(values_x : List, values_y : List, decimal_places : int):
        '''Adding values above the chart columns'''
        for i in range(len(values_x)):
            plt.text(i, round(values_y[i], decimal_places), round(values_y[i], decimal_places), ha = 'center', bbox = dict(facecolor = 'red', alpha =.8))
