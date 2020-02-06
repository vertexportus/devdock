from pprint import pp

import yaml
from dict_deep import deep_get

from utils import env
from utils.templates import Templates
from .project import Project
from .project_config_data import ProjectConfigData
from .project_repo import ProjectRepo
from .service import Service


class ProjectConfig(ProjectConfigData):
    @classmethod
    def load(cls):
        with open(env.project_config_file_path(), 'r') as stream:
            return cls(yaml.load(stream, Loader=yaml.FullLoader))

    def __init__(self, data):
        with open(env.devdock_path('docker/defaults.yaml')) as stream:
            self.defaults = yaml.load(stream, Loader=yaml.FullLoader)
        self.templates = Templates(env.docker_template_path())
        self.docker = data['docker'] if 'docker' in data else {}
        self.projects = {k: Project(k, master=self, data=v) for k, v in
                         data['projects'].items()} if 'projects' in data and type(data['projects']) is dict else {}
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

    def get_container_name_by_path(self, simple_path):
        container = None
        if '.' in simple_path:
            projects = self.projects
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
            if service and len(service.containers) > 0:
                container = service.containers[next(iter(service.containers))]
        return container.fullname if container else None

    def get_compose(self):
        compose_version = deep_get(self.docker, 'compose.version')
        if compose_version and float(compose_version) < deep_get(self.defaults, 'docker-compose.version.minimum'):
            raise Exception(f"devdock requires at least version "
                            f"{deep_get(self.defaults, 'docker-compose.version.minimum')} "
                            f"for docker-compose format")
        compose = {
            'version': compose_version if compose_version else str(
                deep_get(self.defaults, 'docker-compose.version.auto')),
            'services': {},
            'volumes': {}
        }
        for service in self.services.values():
            service.generate_compose(compose)
        for project in self.projects.values():
            for project_service in project.services.values():
                project_service.generate_compose(compose)
        return compose

    def get_env(self):
        envs = []
        for service in self.services.values():
            envs += service.get_env()
        for project in self.projects.values():
            for project_service in project.services.values():
                envs += project_service.get_env()
        return list(dict.fromkeys(envs))
