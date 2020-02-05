from pprint import pp

import yaml
from dict_deep import deep_get

from utils import env
from .project import Project
from .project_config_data import ProjectConfigData
from .project_repo import ProjectRepo
from .service import Service


class ProjectConfig(ProjectConfigData):
    MINIMUM_DOCKER_COMPOSE_VERSION = 3.0
    AUTO_DOCKER_COMPOSE_VERSION = 3.7

    @classmethod
    def load(cls):
        with open(env.project_config_file_path(), 'r') as stream:
            return cls(yaml.load(stream, Loader=yaml.FullLoader))

    def __init__(self, data):
        self.docker = data['docker'] if 'docker' in data else {}
        self.projects = {k: Project(k, master=self, data=v) for k, v in data['projects'].items()}
        self.services = {k: Service(k, master=self, project=None, data=v) for k, v in
                         data['services'].items()} if 'services' in data else {}
        self.devdock = ProjectRepo(None, data['devdock'])
        for service in self.services.values():
            service.update_references()
        for project in self.projects.values():
            for project_service in project.services.values():
                project_service.update_references()

    def get_service_by_path(self, service_path):
        if '.' in service_path:
            [project_name, service_name] = service_path.split('.')
            if project_name in self.projects:
                project = self.projects[project_name]
                return project.services[service_name] if service_name in project.services else None
            else:
                return None
        else:
            service = self.services[service_path] if service_path in self.services else None
            if service:
                return service
            else:
                if service_path in self.projects:
                    project = self.projects[service_path]
                    return project.services[service_path] if service_path in project.services else None

    def get_compose(self, for_env):
        compose_version = deep_get(self.docker, 'compose.version')
        if compose_version and float(compose_version) < self.MINIMUM_DOCKER_COMPOSE_VERSION:
            raise Exception(f"devdock requires at least version {self.MINIMUM_DOCKER_COMPOSE_VERSION} "
                            f"for docker-compose format")
        compose = {
            'version': compose_version if compose_version else str(self.AUTO_DOCKER_COMPOSE_VERSION),
            'services': {},
            'volumes': {}
        }
        for service in self.services.values():
            service.generate_compose(compose, for_env)
        for project in self.projects.values():
            for project_service in project.services.values():
                project_service.generate_compose(compose, for_env)
        return compose

    def get_env(self):
        envs = []
        for service in self.services.values():
            envs += service.get_env()
        for project in self.projects.values():
            for project_service in project.services.values():
                envs += project_service.get_env()
        return list(dict.fromkeys(envs))
