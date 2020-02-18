from .container_template import ContainerTemplate
from utils.yaml_template_object import YamlTemplateObject


class ServiceTemplate(YamlTemplateObject):
    hidden_fields = ['service']
    yaml_tag = '!ServiceTemplate'
    name: str
    base_path: str
    containers: dict

    def __init__(self, service, name):
        self.service = service
        self.name = name
        self.base_path = name.replace('.', '/')
        templates = service.master.templates
        template_params = {
            'service': service
        }
        super().__init__(
            templates=templates,
            template_params=template_params,
            template_name=f"{self.base_path}/config.yaml"
        )
        self.containers = {k: ContainerTemplate(k, self, templates, template_params, v)
                           for k, v in self.try_get('containers', {}).items()}
