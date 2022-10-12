#pylint: disable=C0303 E0401

'''Controlling main module, called directly from the command line'''

import sys
from loguru import logger
from tools.CommandParser import CommandParser
from tools.subparsers.ShowSubParser import ShowSubParser

__VERSION__ = "0.3.0"


if __name__ == "__main__":
    parser = CommandParser.create_parser()
    namespace = parser.parse_args(sys.argv[1:])
 
    if namespace.command == "show":
        ShowSubParser.run_show(namespace)

else:
    logger.error("Marp was called as a module from another file, such use is not possible")
