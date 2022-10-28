#pylint: disable=C0303 E0401

'''
marp - MaidReadingsProcessor (Maid Software's processing utility)
Written by Ggorets0dev (nikgorets4work@gmail.com)
Version: 0.12.0
GitHub: https://github.com/Ggorets0dev/maid-readings-processor
License: MIT
'''

__VERSION__ = "0.12.0"

import sys
import pyfiglet
from models.exceptions import CalledAsModuleError, exception_hook
from tools.CommandParser import CommandParser
from tools.subparsers.ShowSubParser import ShowSubParser
from tools.subparsers.CheckSubParser import CheckSubParser
from tools.subparsers.ReduceSubParser import ReduceSubParser
from tools.subparsers.CalcSubParser import CalcSubParser
from tools.subparsers.TemplatesSubParser import TemplatesSubParser
from tools.subparsers.SplitSubParser import SplitSubParser

# NOTE - Assigning a more user-friendly exception output 
sys.excepthook = exception_hook

if __name__ == "__main__":
    namespace = CommandParser.create_parser().parse_args(sys.argv[1:])

    if namespace.version or namespace.command is None:
        print(pyfiglet.figlet_format('marp', font = 'ogre'), end='')
        print(f"Version: {__VERSION__}")
        print("Developer: Ggorets0dev (nikgorets4work@gmail.com)")
        print("GitHub: https://github.com/Ggorets0dev/maid-readings-processor")

    #SECTION - Processing commands from subparsers
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
    # !SECTION

else:
    raise CalledAsModuleError
