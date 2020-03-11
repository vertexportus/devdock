import yaml
from copy import deepcopy

from dict_deep import deep_get


class YamlDataObject(yaml.YAMLObject):
    base_hidden_fields = ['_data']
    hidden_fields = []
    yaml_tag = "!YamlDataObject"
    _data: dict

    @staticmethod
    def load(file_path) -> dict:
        with open(file_path, 'r') as stream:
            return yaml.load(stream, Loader=yaml.FullLoader)

    def __init__(self, file_path=None, data=None):
        if file_path:
            self.load_data(file_path)
        elif data:
            self._data = data
        else:
            raise Exception(f"either file_path or data need to be set on constructor for '{self.__class__}'")

    def load_data(self, file_path):
        self._data = self.load(file_path)

    def try_get(self, prop, default):
        if '.' in prop:
            value = deep_get(self._data, prop)
            return value if value else default
        else:
            return self._data[prop] if prop in self._data else default

    def get_required(self, prop):
        if prop not in self._data:
            raise Exception(f"property {prop} does not exist in data. {self}")
        return self._data[prop]

    @classmethod
    def to_yaml(cls, dumper, data):
        new_data = deepcopy(data)
        for item in cls.base_hidden_fields + cls.hidden_fields:
            if item in new_data.__dict__:
                del new_data.__dict__[item]
        return dumper.represent_yaml_object(cls.yaml_tag, new_data, cls, flow_style=cls.yaml_flow_style)
