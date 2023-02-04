'''
Marp - MaidReadingsProcessor (Maid Software's processing utility)
Written by Ggorets0dev (nikgorets4work@gmail.com)
Version: 0.28.0
License: MIT
GitHub: https://github.com/Ggorets0dev/maid-readings-processor
'''

__VERSION__ = "0.28.0"

import sys
import pyfiglet
from colorama import init
from models.exceptions import CalledAsModuleError, user_exception_hook
from tools.CommandParser import CommandParser
from tools.subparsers.ShowSubParser import ShowSubParser
from tools.subparsers.CheckSubParser import CheckSubParser
from tools.subparsers.ReduceSubParser import ReduceSubParser
from tools.subparsers.CalcSubParser import CalcSubParser
from tools.subparsers.TemplateSubParser import TemplateSubParser
from tools.subparsers.SplitSubParser import SplitSubParser
from tools.subparsers.AliasSubParser import AliasSubParser
from tools.subparsers.GraphSubParser import GraphSubParser

# NOTE - Colorama initialization
init()

# NOTE - Assigning a more user-friendly exception output 
sys.excepthook = user_exception_hook

if __name__ == "__main__":
    parser = CommandParser.create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    if namespace.version:
        print(pyfiglet.figlet_format('marp', font = 'ogre'), end='')
        print(f"Version: {__VERSION__}")
        print("Developer: Ggorets0dev (nikgorets4work@gmail.com)")
        print("GitHub: https://github.com/Ggorets0dev/maid-readings-processor")

    # SECTION - Processing commands from subparsers
    elif namespace.command == 'show':
        ShowSubParser.run_show(namespace)
    
    elif namespace.command == 'check':
        CheckSubParser.run_check(namespace)

    elif namespace.command == 'reduce':
        ReduceSubParser.run_reduce(namespace)

    elif namespace.command == 'calc':
        CalcSubParser.run_calc(namespace)

    elif namespace.command == 'template':
        TemplateSubParser.run_templates(namespace)

    elif namespace.command == 'split':
        SplitSubParser.run_split(namespace)

    elif namespace.command == 'alias':
        AliasSubParser.run_alias(namespace)

    elif namespace.command == 'graph':
        GraphSubParser.run_graph(namespace)
    # !SECTION

    elif not namespace.command:  
        parser.print_help()

else:
    raise CalledAsModuleError
