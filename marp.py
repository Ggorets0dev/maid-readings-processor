#pylint: disable=C0303 E0401

'''Controlling main module, called directly from the command line'''

import sys
import pyfiglet
from loguru import logger
from tools.CommandParser import CommandParser
from tools.subparsers.ShowSubParser import ShowSubParser
from tools.subparsers.CheckSubParser import CheckSubParser
from tools.subparsers.ReduceSubParser import ReduceSubParser
from tools.subparsers.CalcSubParser import CalcSubParser
from tools.subparsers.TemplatesSubParser import TemplatesSubParser
from tools.subparsers.SplitSubParser import SplitSubParser

__VERSION__ = "0.10.0"


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

    elif namespace.command == "reduce":
        ReduceSubParser.run_reduce(namespace)

    elif namespace.command == "calc":
        CalcSubParser.run_calc(namespace)

    elif namespace.command == "templates":
        TemplatesSubParser.run_templates(namespace)

    elif namespace.command == "split":
        SplitSubParser.run_split(namespace)

else:
    logger.error("Marp was called as a module from another file, such use is not available")
