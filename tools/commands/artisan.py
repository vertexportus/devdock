import argparse

from commands import base_command


class Artisan(base_command.BaseCommand):
    @staticmethod
    def argparse(parser, subparsers):
        parser_main = subparsers.add_parser('artisan', help="runs artisan inside a laravel container")
        parser_main.add_argument('-p', '--project', nargs="?", help="set laravel project to run composer on")
        parser_main.add_argument('params', nargs=argparse.REMAINDER, help='artisan parameters')

    def process_command(self):
        pass
