import os
import re
import shutil

import yaml

from commands import base_command
from project import ProjectConfigManager
from utils import env
from utils.colors import *


class Config(base_command.BaseCommand):
    @staticmethod
    def argparse(parser, subparsers):
        parser_main = subparsers.add_parser('config', help="environment and project config helper")
        subparser = parser_main.add_subparsers(required=True, dest="config_command", help="config sub-commands")
        parser_init = subparser.add_parser('init', help="initializes a new dev environment")
        parser_init.add_argument('-r', '--repo', nargs="?", default="git@github.com:vertexportus/devdock.git",
                                 help="devdock repository to use")
        if ProjectConfigManager.config_exists():
            parser_docker = subparser.add_parser('docker', help="generates docker config")
            parser_docker.add_argument('-g', '--generate', action="store_true", help="generate docker config")
            parser_docker.add_argument('-p', '--print', action="store_true", help="print docker config on console on "
                                                                                  "generate")
            parser_docker.add_argument('-e', '--env', nargs="?", default=env.env(),
                                       help="generate docker config for specific env")
            parser_env = subparser.add_parser('env', help="manages env configs")
            parser_env.add_argument('-g', '--generate', action="store_true", help="generate/update env files")
            parser_hosts = subparser.add_parser('hosts', help="generates host information")

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

    def _init_handler(self):
        project_file = env.project_config_file_path()
        if os.path.isfile(project_file):
            raise Exception('project.yaml file already exists for this project')
        project_config = {'devdock': {}, 'projects': {}}
        project_repo_raw = self.args.repo
        repo_config_key = 'github'
        if '@github.com:' in project_repo_raw:
            match = re.findall(r"@github\.com:([\w/]+\.git)", project_repo_raw)
            if len(match) > 0:
                project_repo = match[0]
            else:
                raise Exception("error trying to parse repo")
        elif 'https://github.com/' in project_repo_raw:
            project_repo = project_repo_raw.replace('https://github.com/', 1)
        else:
            repo_config_key = 'repo'
            project_repo = project_repo_raw
        project_config['devdock'][repo_config_key] = project_repo
        with open(project_file, "w") as stream:
            stream.write(yaml.dump(project_config))

    def _hosts_handler(self):
        regex = re.compile(r"\d+\.\d+\.\d+\.\d+\s+([\w.]+)\s+#\s" + env.project_name() + r"\scommand\sregistry")
        with open("/etc/hosts", "r") as stream:
            hosts_config = stream.read()
        matches = regex.findall(hosts_config)
        if len(matches) == 0:
            self.run_shell(f"echo \"127.0.0.1  {env.project_name()}.local # {env.project_name()} command registry\" | sudo tee -a /etc/hosts")
            print(green("hosts configured properly"))
        else:
            print(yellow(f"hosts already configured for this project with url: {next(iter(matches))}"))
