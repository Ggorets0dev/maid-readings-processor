'''AliasSubParser location'''

import os
import sys
import subprocess
from copy import copy
from argparse import _SubParsersAction, Namespace
from colorama import Fore, Style
from loguru import logger
from tools.FileParser import FileParser
from tools.display_utils import ConstantValueOutput, Color

class AliasSubParser:
    '''Processing aliases for commands'''

    @classmethod
    def add_subparser(cls, subparsers: _SubParsersAction) -> _SubParsersAction:
        '''Creating a subparser'''
        alias_subparser = subparsers.add_parser('alias', description='Processing aliases for commands, created by user')
        alias_subparser.add_argument('-s', '--show', action='store_true', help='Show all available aliases')
        alias_subparser.add_argument('-a', '--add', nargs=2, help='Add an alias (specify NAME and COMMAND; enter the subparser and its arguments as a command, the python interpreter and the name of the main script will be added automatically after launch call)')
        alias_subparser.add_argument('-l', '--launch', nargs=1, help='Launch an alias (specify NAME)')
        alias_subparser.add_argument('-d', '--delete', nargs=1, help='Delete an alias (specify NAME)')
        alias_subparser.add_argument('-r', '--reset', action='store_true', help='Delete aliases file (all aliases)')
        cls.SUBPARSER = alias_subparser
        return subparsers

    @classmethod
    def run_alias(cls, namespace: Namespace) -> None:
        '''Run if Alias subparser was called'''
        ALIASES_PATH = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..', '..', 'aliases.yaml')
        MAIN_SCRIPT_PATH = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..', '..', 'marp.py')
        
        ALIASES = FileParser.parse_aliases(ALIASES_PATH)

        if namespace.show:
            if ALIASES['exists']:
                Color.cprint("All available aliases: ", fore=Fore.WHITE, style=Style.BRIGHT, end='\n')
                for alias in ALIASES['data']:
                    ConstantValueOutput(alias['name'], f"python marp.py {alias['cmd']}").display()
            else:
                logger.info("No alias file (create an alias using --add)")
                return

        elif namespace.add:
            name, command = namespace.add[0], namespace.add[1]

            aliases = copy(ALIASES['data'])
            for alias in aliases:
                if alias['name'] == name:
                    logger.error("Failed to add an alias, the name is already taken (firstly remove it with --delete)")
                    return

            aliases.append( { 'name': name, 'cmd': command } )

            FileParser.save_aliases(ALIASES_PATH, aliases)
            logger.success(f"Alias {name} successfully added")

        elif namespace.launch:
            if not ALIASES['exists']:
                logger.info("No alias file (create an alias using --add)")
                return
                
            elif len(ALIASES['data']) == 0:
                logger.error(f"Failed to retrieve aliases from file {ALIASES_PATH} (clean up aliases with --reset or delete file manually)")
                return 

            try:
                alias_activated = False
                for alias in ALIASES['data']:
                    if alias['name'] == namespace.launch[0]:
                        alias_activated = True
                        subprocess.run(f"{sys.executable} {MAIN_SCRIPT_PATH} {alias['cmd']}", check=True)
                        break
                if not alias_activated:
                    logger.info("Failed to find an alias for the specified name")
            except KeyError:
                logger.error(f"Failed to retrieve aliases from file {ALIASES_PATH} (clean up aliases with --reset or delete file manually)")

        elif namespace.delete:
            name = namespace.delete[0]

            aliases = copy(ALIASES['data'])
            for inx, alias in enumerate(aliases):
                if alias['name'] == name:
                    aliases.pop(inx)
                    if len(aliases) != 0:
                        FileParser.write_aliases(ALIASES_PATH, aliases)
                        logger.success(f"Successfully deleted an alias {name}")
                    else:
                        os.remove(ALIASES_PATH) 
                        logger.success("Successfully deleted an alias, since there are no more of them left, the file is also deleted")
                    return
            logger.error("Couldn't find an alias")

        elif namespace.reset:
            if os.path.isfile(ALIASES_PATH): 
                os.remove(ALIASES_PATH) 
                logger.success("Alias file has been successfully deleted")
            else: 
                logger.error("No alias file, no deletion possible (new aliases can be created using --add)")
            
        else:
            logger.error("Alias interraction not selected")
            cls.SUBPARSER.print_help()
