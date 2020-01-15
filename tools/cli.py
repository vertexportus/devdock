#!/usr/bin/env python3

import sys
import inspect
import importlib
import traceback
import utils.colors
from utils import env, ColoredArgumentParser


command_modules = {
    "docker",
    "shell",
    "git",
    "config",
}


def cli():
    # parse top level commands
    parser = ColoredArgumentParser(prog=env.cli_command(), description='project dev utilities')
    parser.add_argument('-v', '--verbose', action="store_true", help="verbose output")
    subparsers = parser.add_subparsers(required=True, dest="command", help=f"{env.cli_command()} command",
                                       title="commands")

    # parse additional modules
    parser_classes = dict()
    for command in command_modules:
        class_ref = None
        module = importlib.import_module(f"commands.{command}")
        classes = inspect.getmembers(module, inspect.isclass)
        if len(classes) < 1:
            print(utils.colors.red(f"module commands.{command} contains no classes - this is ilegal"))
            exit(1)
        for class_inspect in classes:
            class_name = class_inspect[0]
            class_name_should_be = ''.join(word.title() for word in command.split('_'))
            if class_name == class_name_should_be:
                class_ref = class_inspect[1]
                break
        if class_ref is None:
            print(utils.colors.red(
                f"module commands.{command} contains no classes with appropriate name (should be a CamelCase of the file's snake_case)"))
            exit(1)
        class_ref.argparse(parser, subparsers)
        parser_classes[command] = class_ref

    # parse args and exec appropriate command
    args = parser.parse_args()
    global verbose
    verbose = args.verbose
    command = parser_classes[args.command](args)
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
