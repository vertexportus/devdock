import argparse

from commands import base_command


class Laravel(base_command.BaseCommand):
    @staticmethod
    def argparse(parser, subparsers):
        parser_main = subparsers.add_parser('laravel', help="runs artisan inside a laravel container")
        parser_main.add_argument('-p', '--project', nargs="?", help="set laravel project to run composer on")
        parser_main.add_argument('params', nargs=argparse.REMAINDER, help='artisan parameters')

    def process_command(self):
        project = self.get_project_by_name_or_default_by_tech(self.args.project, 'laravel')
        container = project.get_container_by_stack('laravel')
        if container is None:
            raise Exception(f"container not found by stack")
        params = ' '.join(self.args.params) if len(self.args.params) else ''
        self.container_exec_run(container.fullname, f"php artisan {params}")
