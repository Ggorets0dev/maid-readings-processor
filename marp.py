'''Controlling main module, called directly from the command line'''

__VERSION__ = "0.1.0"

from tools.FileParser import FileParser

if __name__ == "__main__":
    FileParser.reduce_readings(file_path='english_names.txt')
