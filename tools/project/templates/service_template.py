from utils.yaml_template_object import YamlTemplateObject


class ServiceTemplate(YamlTemplateObject):
    hidden_fields = ['service']
    yaml_tag = '!ServiceTemplate'
    name: str
    base_path: str

    def __init__(self, service, name):
        self.service = service
        self.name = name
        self.base_path = name.replace('.', '/')
        super().__init__(
            templates=service.master.templates,
            template_params={
                'service': service
            },
            template_name=f"{self.base_path}/config.yaml"
        )
