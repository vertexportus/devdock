from .templates.service_template import ServiceTemplate
from utils.yaml_data_object import YamlDataObject


class Service(YamlDataObject):
    hidden_fields = ['project', 'master']
    yaml_tag = '!Service'
    name: str
    # database: str
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
        # self.database = self.try_get('database', None)
        self.version = self.try_get('version', None)
        self.ports = self.try_get('ports', False)
        self.env_prefix = self.try_get('env_prefix', name.upper())
        self.env_files = self.try_get('env_files', False)
        self.template = ServiceTemplate(service=self, name=self.get_required('template'))
