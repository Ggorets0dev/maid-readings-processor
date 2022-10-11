'''Controlling main module, called directly from the command line'''

from loguru import logger
from tools.FileParser import FileParser

__VERSION__ = "0.2.0"

if __name__ == "__main__":
    print(FileParser.parse_readings(file_path='BLOCKS.TXT'))
else:
    logger.error("Marp was called as a module from another file, such use is not possible")
