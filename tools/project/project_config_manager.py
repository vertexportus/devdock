import os
from pprint import pp

import yaml

from .project_config import ProjectConfig
from utils import env


class ProjectConfigManager:
    def __init__(self):
        self._config = ProjectConfig.load()

    def get_projects(self):
        return self._config.projects

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

    def get_service_by_path(self, service_path):
        return self._config.get_service_by_path(service_path)

    def get_container_name_by_simple_path(self, simple_path):
        if '.' in simple_path:
            projects = self.get_projects()
            [base, path] = simple_path.split('.', 1)
            if base in projects:
                project = projects[base]
                if base in project.services:
                    service = project.services[base]
                    container = service.containers[path]
                else:
                    if '.' in path:
                        [service_name, container_name] = path.split('.')
                        service = project.services[service_name]
                        container = service.containers[container_name] if service else None
                    else:
                        service = project.services[path]
                        container = service.containers[next(iter(service.containers))]
            else:
                service = self.get_service_by_path(base)
                container = service.containers[path]
        else:
            service = self.get_service_by_path(simple_path)
            container = service.containers[next(iter(service.containers))]
        return container.fullname

    def get_env(self):
        return self._config.get_env()
