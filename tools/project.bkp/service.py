import re

from .service_data import ServiceData
from .templates.service_template import ServiceTemplate


class Service(ServiceData):
    def __init__(self, name, master, project, data):
        super().__init__(name, master, project, data)
        self.env_prefix = self.try_get('env_prefix', self.fullname)
        self.env_files = self.try_get('env_files', False)
        self.database = self.try_get('database', None)
        self.version = self.try_get('version', None)
        self.ports = self.try_get('ports', False)
        self.targets = self.try_get('targets', {})
        self.template = ServiceTemplate(data['template'], service=self)

    def generate_compose(self, compose):
        self.template.generate_compose(compose)

    def get_env(self) -> list:
        envs = []
        r = re.compile(r"\${*([A-Z_]+)}*")
        for container in self.template.containers.values():
            envs += list(map(lambda e: r.findall(e)[0], container.env.environment.values()))
        return envs

    def get_container_dependencies(self):
        dependencies = []
        if self.database:
            service = self.master.get_service_by_path(self.database)
            if service:
                for service_container in service.template.containers.values():
                    dependencies.append(service_container.fullname)
        return dependencies

    def update_references(self):
        self.template.update_references()
