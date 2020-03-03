from utils import env
from .container_template import ContainerTemplate
from utils.yaml_template_object import YamlTemplateObject
from ..generation import generate_build_files


class ServiceTemplate(YamlTemplateObject):
    hidden_fields = ['service']
    yaml_tag = '!ServiceTemplate'
    name: str
    base_path: str or list
    containers: dict

    @property
    def is_single_container(self) -> bool:
        return len(self.containers) < 2

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

    def post_load_init(self):
        for container in self.containers.values():
            container.post_load_init()

    def generate_compose(self, compose_services, compose_volumes):
        for container in self.containers.values():
            container.generate_compose(compose_services, compose_volumes)
        self.generate_build_files()

    def generate_build_files(self):
        template_params = {
            'defaults': self.service.master.defaults,
            'project': self.service.project,
            'service': self.service,
            'siblings': self.containers
        }
        dest_path = f"build/{self.service.master.current_env}"
        paths = list(map(lambda x: f"{x}/build", self.base_path if type(self.base_path) == list else [self.base_path]))
        generate_build_files(paths, dest_path, self.templates, **template_params)
