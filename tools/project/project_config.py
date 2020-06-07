from dict_deep import deep_get

from utils import env
from utils.templates import Templates
from utils.yaml_data_object import YamlDataObject
from .project import Project
from .project_repo import ProjectRepo
from .service import Service


class ProjectConfig(YamlDataObject):
    yaml_tag = '!ProjectConfig'
    hidden_fields = ['templates', 'defaults']
    current_env = env.env()
    defaults: dict
    templates: Templates
    docker: dict
    projects: dict
    services: dict
    devdock: ProjectRepo

    def __init__(self):
        super().__init__(file_path=env.project_config_file_path())
        self.defaults = self.load(env.devdock_path('docker/defaults.yaml'))
        self.templates = Templates(env.docker_template_path(), project_config=self)
        self.docker = self.try_get('docker', {})
        self.devdock = ProjectRepo(None, self.get_required('devdock'))
        self.projects = {k: Project(k, master=self, data=v) for k, v in self.try_get('projects', {}).items()}
        self.services = {k: Service(k, master=self, data=v) for k, v in self.try_get('services', {}).items()}
        # container names
        for service in self.services.values():
            service.define_container_names()
        for project in self.projects.values():
            project.define_container_names()
        # post load init
        for service in self.services.values():
            service.post_load_init()
        for project in self.projects.values():
            project.post_load_init()

    def get_compose(self, for_env):
        self.current_env = for_env
        compose = {
            'version': self.get_compose_version(),
            'services': {},
            'volumes': {}
        }
        for service in self.services.values():
            service.generate_compose(compose['services'], compose['volumes'])
        for project in self.projects.values():
            project.generate_compose(compose['services'], compose['volumes'])
        return compose

    def get_compose_version(self):
        compose_version = deep_get(self.docker, 'compose.version')
        if compose_version:
            if float(compose_version) < deep_get(self.defaults, 'docker-compose.version.minimum'):
                raise Exception(f"devdock requires at least version "
                                f"{deep_get(self.defaults, 'docker-compose.version.minimum')} "
                                f"for docker-compose format")
        else:
            compose_version = str(deep_get(self.defaults, 'docker-compose.version.auto'))
        return compose_version

    def get_container_by_path(self, container_path):
        container = None
        if '.' in container_path:
            raise Exception(f"TODO: get_container_by_path with . path {container_path=}")
        else:
            if container_path in self.services:
                container = self.services[container_path].get_container_by_path(container_path)
            elif container_path in self.projects:
                if container_path in self.projects[container_path].services:
                    container = self.projects[container_path].services[container_path] \
                        .get_container_by_path(container_path)
        if not container:
            raise Exception(f"can't find container by path '{container_path}'")
        return container

    def get_container_name_by_path(self, container_path):
        return self.get_container_by_path(container_path).fullname

    def get_container_templates(self):
        container_templates = {}
        for project in self.projects.values():
            for service in project.services.values():
                container_templates = {**container_templates, **{v.fullname: v for v in service.get_container_templates().values()}}
        for service in self.services.values():
            container_templates = {**container_templates, **{v.fullname: v
                                                             for v in service.get_container_templates().values()}}
        return container_templates
