#pylint: disable=C0303 E0401

'''Controlling main module, called directly from the command line'''

import sys
import pyfiglet
from loguru import logger
from tools.CommandParser import CommandParser
from tools.subparsers.ShowSubParser import ShowSubParser
from tools.subparsers.CheckSubParser import CheckSubParser

__VERSION__ = "0.5.0"


if __name__ == "__main__":
    namespace = CommandParser.create_parser().parse_args(sys.argv[1:])

    if namespace.version or namespace.command is None:
        print(pyfiglet.figlet_format('marp', font = 'ogre'), end='')
        print(f"Version: {__VERSION__}")
        print("Developer: Ggorets0dev <nikgorets4work@gmail.com>")
        print("GitHub: https://github.com/Ggorets0dev/maid-readings-processor")

    elif namespace.command == "show":
        ShowSubParser.run_show(namespace)
    
    elif namespace.command == "check":
        CheckSubParser.run_check(namespace)


else:
    logger.error("Marp was called as a module from another file, such use is not available")
