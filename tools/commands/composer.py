import argparse

from commands import base_command
from utils import env


class Composer(base_command.BaseCommand):
    @staticmethod
    def argparse(parser, subparsers):
        parser_main = subparsers.add_parser('composer', help="runs composer inside project folder")
        parser_main.add_argument('-p', '--project', nargs="?", help="set php project to run composer on")
        parser_main.add_argument('params', nargs=argparse.REMAINDER, help='composer parameters')

    def process_command(self):
        if self.args.project:
            project = self.project_config.get_projects_by_name(self.args.project)
            if not project:
                raise Exception(f"project '{self.args.project}' does not exist")
            if 'php' not in project.tech_stack:
                raise Exception(f"project '{self.args.project}' does not support tech 'php'")
        else:
            projects = self.project_config.get_projects_by_tech('php')
            if len(projects) > 1:
                if not self.args.project:
                    raise Exception(f"need to specify php project to run composer on with -p|--project")
            project = projects[0]
        params = ' '.join(self.args.params) if len(self.args.params) else ''
        self.run_shell(
            f"docker run --rm --volume {project.path}:/app composer {params}")
