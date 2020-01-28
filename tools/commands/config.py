import os
import shutil

from commands import base_command
from utils import env


class Config(base_command.BaseCommand):
    @staticmethod
    def argparse(parser, subparsers):
        parser_main = subparsers.add_parser('config', help="environment and project config helper")
        subparser = parser_main.add_subparsers(required=True, dest="config_command", help="config sub-commands")
        parser_docker = subparser.add_parser('docker', help="generates docker config")
        parser_docker.add_argument('-g', '--generate', action="store_true", help="generate docker config")
        parser_docker.add_argument('-p', '--print', action="store_true", help="print docker config on console on "
                                                                              "generate")
        parser_docker.add_argument('-e', '--env', nargs="?", default=env.env(),
                                   help="generate docker config for specific env")
        parser_env = subparser.add_parser('env', help="manages env configs")
        parser_env.add_argument('-g', '--generate', action="store_true", help="generate/update env files")

    def process_command(self):
        getattr(self, f"_{self.args.config_command}_handler")()

    def _docker_handler(self):
        if self.args.generate:
            self.project_config.generate_docker(self.args.print, self.args.env)

    def _env_handler(self):
        base_vars = [
            'PROJECT_PATH',
            'PROJECT_NAME',
            'GIT_USE_SSH',
        ]
        envs = base_vars + self.project_config.get_env()
        envrc_file_path = env.project_path(".envrc")
        if self.args.generate or not os.path.exists(envrc_file_path):
            shutil.copy(env.env_template_path("direnv"), envrc_file_path)
            self.run_shell("direnv allow")
        for e in envs:
            print(f"{e}: {os.environ[e] if e in os.environ else '<none>'}")
