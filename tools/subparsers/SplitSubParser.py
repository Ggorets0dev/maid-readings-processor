#pylint: disable=C0303 C0301 E0401 E0611

from argparse import _SubParsersAction, Namespace, FileType
from loguru import logger
from tools.FileParser import FileParser

class SplitSubParser:
    '''Displaying stitched patterns for headers and readings'''

    @staticmethod
    def add_subparser(subparsers : _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        split_subparser = subparsers.add_parser('split', description='Split file by parts or line count for better performance (check and reducing are disabled)')
        split_subparser.add_argument('-i', '--input', nargs=1, type=FileType(encoding='UTF-8'), required=True, help='Path to the file with readings')

        # NOTE - Set mode of split
        split_subparser.add_argument('-p', '--parts', nargs=1, type=int, help='Divide the file into PARTS of equal parts (max: 1000)')
        split_subparser.add_argument('-l', '--lines', nargs=1, type=int, help='Divide the file into files with LINES of lines in each one')
        return subparsers

    @staticmethod
    def run_split(namespace : Namespace) -> None:
        '''Run if Split subparser was called'''
        lines_cnt = FileParser.count_lines(file_path=namespace.input[0].name)

        # SECTION - Processing targets: --parts --lines
        if namespace.parts:
            if namespace.parts[0] >= 2 and namespace.parts[0] <= 1000 and namespace.parts[0] < lines_cnt:
                part_size = int(lines_cnt / namespace.parts[0])
                created_parts_cnt = FileParser.split_file(file_path=namespace.input[0].name, part_size=part_size)
                
                if created_parts_cnt != namespace.parts[0]:
                    logger.warning(f"File could not be divided into {namespace.parts[0]} parts, because there were fewer headers, {created_parts_cnt} files were created")

            else:
                logger.error(f"Count of --parts must be more than 1 and less than count of lines in file ({lines_cnt}) and 1000")
                return
            

        elif namespace.lines:
            if namespace.lines[0] >= 2 and namespace.lines[0] < lines_cnt:
                part_size = namespace.lines[0]
                created_parts_cnt = FileParser.split_file(file_path=namespace.input[0].name, part_size=part_size)

                if created_parts_cnt != lines_cnt / namespace.lines[0] and lines_cnt % namespace.lines[0] == 0:
                    logger.warning(f"File could not be divided into parts with {namespace.lines[0]} lines in every file, because there were fewer headers, {created_parts_cnt} files were created")

            else:
                logger.error(f"Count of --lines must be more than 1 and less than count of lines in file ({lines_cnt})")
                return
        else:
            logger.error("Split mode not selected (--parts / --lines)")
            return
        # !SECTION