from copy import deepcopy

from deepmerge import always_merger

from utils.templates import Templates
from utils.yaml_data_object import YamlDataObject


class YamlTemplateObject(YamlDataObject):
    base_hidden_fields = ['_data', 'templates', 'template_params']
    yaml_tag = "!YamlTemplateObject"
    templates: Templates
    template_params: dict

    def __init__(self, templates, template_params, file_path=None, template_name=None, data=None):
        self.templates = templates
        self.template_params = template_params
        if file_path:
            super().__init__(file_path=file_path)
        elif template_name:
            super().__init__(data=self.load_template(template_name))
        elif data:
            super().__init__(data=data)
        else:
            raise Exception("Either file_path or template_name or data must be set on YamlTemplateObject.__init__")

    def load_template_data(self, template_name):
        self._data = self.load_template(template_name)

    def merge_load_template_data(self, template_name):
        self._data = always_merger.merge(self._data, self.load_template(template_name))

    def load_template(self, template_name) -> dict:
        return self.templates.render_template_yaml(template_name, **self.template_params)

    @classmethod
    def to_yaml(cls, dumper, data):
        if hasattr(data, 'templates'):
            templates = data.templates
            data.templates = None
            new_data = deepcopy(data)
            data.templates = templates
        else:
            new_data = deepcopy(data)
        for item in cls.base_hidden_fields + cls.hidden_fields:
            if item in new_data.__dict__:
                del new_data.__dict__[item]
        return dumper.represent_yaml_object(cls.yaml_tag, new_data, cls, flow_style=cls.yaml_flow_style)
