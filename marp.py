#pylint: disable=C0303 E0401

'''Controlling main module, called directly from the command line'''

import sys
import pyfiglet
from loguru import logger
from tools.CommandParser import CommandParser
from tools.subparsers.ShowSubParser import ShowSubParser

__VERSION__ = "0.4.0"


if __name__ == "__main__":
    parser = CommandParser.create_parser()
    namespace = parser.parse_args(sys.argv[1:])
 
    if namespace.version:
        print(f"\n\n{pyfiglet.figlet_format('marp', font = 'ogre')}", end='')
        print(f"Version: {__VERSION__}")
        print("Developer: Ggorets0dev <nikgorets4work@gmail.com>")
        print("GitHub: https://github.com/Ggorets0dev/maid-readings-processor")

    elif namespace.command == "show":
        ShowSubParser.run_show(namespace)

else:
    logger.error("Marp was called as a module from another file, such use is not available")
