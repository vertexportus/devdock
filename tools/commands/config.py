import os
import shutil
from git import Repo, RemoteProgress
from commands import base_command
from utils import env
from utils.colors import *
from project import ProjectConfigManager


class Config(base_command.BaseCommand):
    @staticmethod
    def argparse(parser, subparsers):
        parser_main = subparsers.add_parser('config', help="environment and project config helper")
        subparser = parser_main.add_subparsers(required=True, dest="config_command", help="config sub-commands")
        parser_docker = subparser.add_parser('docker', help="generates docker config")
        parser_docker.add_argument('-g', '--generate', action="store_true", help="generate docker config")
        parser_docker.add_argument('-e', '--env', nargs="?", default=env.env(),
                                   help="generate docker config for specific env")

    def process_command(self):
        getattr(self, f"_{self._args.config_command}_handler")()

    def _docker_handler(self):
        manager = ProjectConfigManager()
        if self._args.generate:
            manager.generate_docker(self._args.env)
            print(blue(f"generated: {env.docker_compose_file_path(self._args.env)}"))
        envs = manager.get_env(self._args.env)
        for service_name, service_vars in envs.items():
            print(green(f"\nService: {service_name}\n"))
            for var in service_vars:
                print(var)
        print('')
