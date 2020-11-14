import argparse

from commands import base_command


class Npm(base_command.BaseCommand):
    @staticmethod
    def argparse(parser, subparsers):
        parser_main = subparsers.add_parser('npm', help="runs npm inside a node container")
        parser_main.add_argument('-p', '--project', nargs="?", help="set node project to run npm on")
        parser_main.add_argument('params', nargs=argparse.REMAINDER, help='npm parameters')

    def process_command(self):
        project = self.get_project_by_name_or_default_by_tech(self.args.project, 'node')
        service = project.get_service_by_tech('node')
        params = ' '.join(self.args.params) if len(self.args.params) else ''
        self.run_shell(f"docker run --rm -v {project.path}:/app "
                       f"--workdir /app node:{service.get_image_version('node')}-alpine yarm {params}")
