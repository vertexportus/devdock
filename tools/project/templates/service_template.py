import os

import yaml

from utils import env
from .container_template import ContainerTemplate
from utils.yaml_template_object import YamlTemplateObject
from ..generation import generate_build_files


class ServiceTemplate(YamlTemplateObject):
    hidden_fields = ['service']
    yaml_tag = '!ServiceTemplate'
    name: str
    base_path: str or list
    entrypoint: str
    containers: dict
    params: dict

    @property
    def is_single_container(self) -> bool:
        return len(self.containers) < 2

    def entrypoint_container(self) -> ContainerTemplate:
        return self.containers[self.entrypoint]

    def __init__(self, service, name):
        self.service = service
        self.name = name
        self.base_path = name.replace('.', '/')
        templates = service.master.templates
        template_params = {
            'defaults': service.master.defaults,
            'project': service.project,
            'service': service
        }
        super().__init__(
            templates=templates,
            template_params=template_params,
            template_name=f"{self.base_path}/config.yaml"
        )
        inherits = self.try_get('inherits', False)
        if inherits:
            self.base_path = [inherits.replace('.', '/'), self.base_path]
            self.merge_load_template_data(f"{self.base_path[0]}/config.yaml")
        self.containers = {k: ContainerTemplate(k, self, templates, template_params, v)
                           for k, v in self.try_get('containers', {}).items()}
        self.entrypoint = self.try_get('entrypoint', next(iter(self.containers.keys())))

    def post_load_init(self):
        template_paths = self.base_path if type(self.base_path) == list else [self.base_path]
        for path in template_paths:
            post_init_file_path = f"{path}/post_init.yaml"
            if os.path.isfile(env.docker_template_path(post_init_file_path)):
                self.merge_load_template_data(post_init_file_path)
        self.params = self.try_get('params', {})
        for container in self.containers.values():
            container.post_load_init()

    def generate_compose(self, compose_services, compose_volumes):
        for container in self.containers.values():
            container.generate_compose(compose_services, compose_volumes)
        self.generate_build_files()

    def generate_build_files(self):
        template_params = {
            **self.params,
            'defaults': self.service.master.defaults,
            'project': self.service.project,
            'service': self.service,
            'siblings': self.containers
        }
        dest_path = (f"build/{self.service.master.current_env}/"
                     f"{self.base_path if type(self.base_path) == str else self.base_path[len(self.base_path) - 1]}")
        paths = list(map(lambda x: f"{x}/build", self.base_path if type(self.base_path) == list else [self.base_path]))
        generate_build_files(paths, dest_path, self.templates, **template_params)
