from .templates.service_template import ServiceTemplate
from utils.yaml_data_object import YamlDataObject


class Service(YamlDataObject):
    hidden_fields = ['project', 'master']
    yaml_tag = '!Service'
    name: str
    database: str
    version: str or dict
    ports: bool or list
    env_prefix: str
    env_files: bool or list
    tech_stack: list
    template: ServiceTemplate

    def __init__(self, name, master, data, project=None):
        super().__init__(data=data)
        self.name = name
        self.master = master
        self.project = project
        self.database = self.try_get('database', None)
        self.version = self.try_get('version', None)
        self.ports = self.try_get('ports', False)
        self.env_prefix = self.try_get('env_prefix', name).upper()
        self.env_files = self.try_get('env_files', False)
        self.tech_stack = []
        self.template = ServiceTemplate(service=self, name=self.get_required('template'))

    def define_container_names(self):
        self.template.define_container_names()

    def post_load_init(self):
        self.template.post_load_init()

    def generate_compose(self, compose_services, compose_volumes):
        self.template.generate_compose(compose_services, compose_volumes)

    def append_tech_stack(self, tech_stack):
        self.tech_stack += tech_stack
        if self.project:
            self.project.append_tech_stack(tech_stack)

    def get_image_version(self, name):
        if self.version:
            if type(self.version) == str or type(self.version) == int:
                return self.version
            elif type(self.version) == dict:
                return self.version[name]
            else:
                raise Exception("version not found")
        else:
            return 'latest'  # self.master.defaults[name]['version']

    def get_container_by_path(self, container_path):
        if container_path == self.name and self.template.is_single_container:
            return next(iter(self.template.containers.values()))
        else:
            if self.template.entrypoint:
                return self.template.containers[self.template.entrypoint]
            else:
                return self.template.containers[container_path] if container_path in self.template.containers else None

    def get_container_by_tech(self, tech):
        return next(iter(filter(lambda x: tech in x.tech_stack, self.template.containers.values())))
