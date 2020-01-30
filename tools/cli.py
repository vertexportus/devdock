#!/usr/bin/env python3

import sys
import inspect
import importlib
import traceback
import utils.colors
from project import ProjectConfigManager
from utils import env, ColoredArgumentParser

command_modules = {
    "docker": None,
    "shell": None,
    "git": None,
    "config": None,
    "composer": 'php',
    "laravel": 'laravel'
}


def cli():
    # parse top level commands
    parser = ColoredArgumentParser(prog=env.cli_command(), description='project dev utilities')
    parser.add_argument('-v', '--verbose', action="store_true", help="verbose output")
    subparsers = parser.add_subparsers(required=True, dest="command", help=f"{env.cli_command()} command",
                                       title="commands")

    # parse additional modules
    parser_classes = dict()
    project_config_manager = ProjectConfigManager() if ProjectConfigManager.config_exists() else None
    for command, command_tech_stack in command_modules.items():
        if not project_config_manager and command != 'config':
            continue
        class_ref = None
        if command_tech_stack and not project_config_manager.is_tech_in_use(command_tech_stack):
            continue
        module = importlib.import_module(f"commands.{command}")
        classes = inspect.getmembers(module, inspect.isclass)
        if len(classes) < 1:
            print(utils.colors.red(f"module commands.{command} contains no classes - this is illegal"))
            exit(1)
        for class_inspect in classes:
            class_name = class_inspect[0]
            class_name_should_be = ''.join(word.title() for word in command.split('_'))
            if class_name == class_name_should_be:
                class_ref = class_inspect[1]
                break
        if class_ref is None:
            print(utils.colors.red(
                (f"module commands.{command} contains no classes with appropriate name "
                 f"(should be a CamelCase of the file's snake_case)")
            ))
            exit(1)
        class_ref.argparse(parser, subparsers)
        parser_classes[command] = class_ref

    # parse args and exec appropriate command
    args = parser.parse_args()
    global verbose
    verbose = args.verbose
    command = parser_classes[args.command](project_config_manager, args)
    command.process_command()


verbose = True
if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        print(utils.colors.red("Interrupted"))
        sys.exit(0)
    except Exception as ex:
        if verbose:
            traceback.print_exc()
        else:
            print(utils.colors.red(ex))
        exit(1)
