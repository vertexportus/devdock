import os

import yaml

from .generation import rebuild_marker_load, rebuild_marker_save, rebuild_marker_reset
from .project_config import ProjectConfig
from utils import env


class ProjectConfigManager:
    @property
    def config(self):
        return self._config

    @staticmethod
    def config_exists():
        return os.path.isfile(env.project_config_file_path())

    def __init__(self):
        self._config = ProjectConfig()
        # print(yaml.dump(self._config))

    def get_projects(self):
        return self._config.projects

    def generate_docker(self, print_console, for_env=env.env()):
        compose = self._config.get_compose(for_env)
        compose_file_path = env.docker_compose_file_path(for_env)
        gen_path = os.path.dirname(compose_file_path)
        if not os.path.isdir(gen_path):
            os.mkdir(gen_path)
        if print_console:
            print(yaml.dump(compose))
        with open(compose_file_path, 'w') as docker_compose_file:
            yaml.dump(compose, docker_compose_file)
        versions_file = env.project_path('.versions')
        if os.path.isfile(versions_file):
            os.remove(versions_file)

    def get_service_by_path(self, service_path):
        return None
        # return self._config.get_service_by_path(service_path)

    def get_container_name_by_simple_path(self, simple_path) -> str:
        return self.config.get_container_name_by_path(simple_path)

    def get_env(self):
        return None
        # return self._config.get_env()

    def is_tech_in_use(self, tech) -> bool:
        for project in self.config.projects.values():
            if tech in project.tech_stack:
                return True
        return False

    def get_projects_by_tech(self, tech) -> list:
        return list(filter(lambda x: tech in x.tech_stack, self.config.projects.values()))

    def get_project_by_name(self, name):
        return self.config.projects[name] if name in self._config.projects else None

    def get_container_templates(self):
        return self.config.get_container_templates()

    @staticmethod
    def get_rebuild():
        return rebuild_marker_load()

    @staticmethod
    def save_rebuild():
        return rebuild_marker_save()

    @staticmethod
    def reset_rebuild():
        return rebuild_marker_reset()
