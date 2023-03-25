'''
Project: Marp - MaidReadingsProcessor (Maid Software's processing utility)
Developer: Ggorets0dev <nikgorets4work@gmail.com>
Version: 0.28.1
License: Apache License 2.0
GitHub: https://github.com/Ggorets0dev/maid-readings-processor
'''

__VERSION__ = "0.28.1"

import sys
import pyfiglet
from colorama import init
from models.exceptions import CalledAsModuleError, user_exception_hook
from tools.command_parser import CommandParser
from tools.subparsers.show_subparser import ShowSubParser
from tools.subparsers.check_subparser import CheckSubParser
from tools.subparsers.reduce_subparser import ReduceSubParser
from tools.subparsers.calc_subparser import CalcSubParser
from tools.subparsers.template_subparser import TemplateSubParser
from tools.subparsers.split_subparser import SplitSubParser
from tools.subparsers.alias_subparser import AliasSubParser
from tools.subparsers.graph_subparser import GraphSubParser

# NOTE - Colorama initialization for Windows
init()

# NOTE - Assigning a more user-friendly exception output 
sys.excepthook = user_exception_hook

if __name__ == "__main__":
    parser = CommandParser.create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    if namespace.version:
        print(pyfiglet.figlet_format('marp', font = 'ogre'), end='')
        print(f"Version: {__VERSION__}")
        print("Developer: Ggorets0dev <nikgorets4work@gmail.com>")
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
