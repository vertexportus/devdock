from utils.templates import Templates
from utils.yaml_template_object import YamlTemplateObject


class ContainerTemplate(YamlTemplateObject):
    hidden_fields = ['service_template']
    yaml_tag = '!ContainerTemplate'
    name: str
    fullname: str

    def __init__(self, name, service_template, templates: Templates, template_params, data):
        super().__init__(templates, template_params, data=data)
        self.name = name
        self.service_template = service_template
