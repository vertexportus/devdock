import os
from pprint import pp

import yaml

from .project_config import ProjectConfig
from utils import env


class ProjectConfigManager:
    def __init__(self):
        self._config = ProjectConfig.load()

    def generate_docker(self, print_console, for_env=env.env()):
        compose = self._config.get_compose(for_env)
        compose_file_path = env.docker_compose_file_path(for_env)
        gen_path = os.path.dirname(compose_file_path)
        if not os.path.isdir(gen_path):
            os.mkdir(gen_path)
        if print_console:
            pp(compose)
        with open(compose_file_path, 'w') as docker_compose_file:
            yaml.dump(compose, docker_compose_file)

    def get_env(self):
        return self._config.get_env()
