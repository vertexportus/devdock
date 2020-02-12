import re
from pprint import pp

from .base_config import BaseConfig
from .project_config_data import ProjectConfigData
from .project_data import ProjectData
from .templates.service_template import ServiceTemplate


class ServiceData(BaseConfig):
    fullname: str
    master: ProjectConfigData
    project: ProjectData
    template: ServiceTemplate
    database: str
    version: str or dict
    ports: bool or list
    env_prefix: str
    env_files: bool or list
    targets: dict
    tech_stack: list

    @property
    def containers(self):
        return self.template.containers

    def __init__(self, name, master, project, data):
        super().__init__(name, data)
        self.fullname = name
        self.master = master
        self.project = project
        self.tech_stack = []

    def __str__(self):
        return f"service {self.name} ({self.fullname})\n    template: {self.template}"

    def __getitem__(self, item):
        return getattr(self, item)

    def data_hasattr(self, attr):
        return attr in self._original_data

    def data_getattr(self, attr):
        return self._original_data[attr]

    def append_to_tech_stack(self, stack):
        self.tech_stack += stack
        if self.project and len(self.tech_stack) > 0:
            self.project.append_to_tech_stack(stack)
