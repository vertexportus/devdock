import argparse

from commands import base_command


class Composer(base_command.BaseCommand):
    @staticmethod
    def argparse(parser, subparsers):
        parser_main = subparsers.add_parser('composer', help="runs composer inside project folder")
        parser_main.add_argument('-p', '--project', nargs="?", help="set php project to run composer on")
        parser_main.add_argument('params', nargs=argparse.REMAINDER, help='composer parameters')

    def process_command(self):
        project = self.get_project_by_name_or_default_by_tech(self.args.project, 'php')
        params = ' '.join(self.args.params) if len(self.args.params) else ''
        self.run_shell(
            f"docker run --rm --volume {project.path}:/app composer {params}")
