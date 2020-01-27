import yaml
from deepmerge import always_merger

from utils import env
from ..base_config import BaseConfig


class ServiceTemplateData(BaseConfig):
    file_path: str or list
    required: list
    containers: dict
    has_single_container: bool

    def __init__(self, name, service):
        self.service = service
        self.file_path = env.docker_template_path(f"config/{name}.yaml")
        with open(self.file_path, 'r') as stream:
            raw_data = yaml.load(stream, Loader=yaml.FullLoader)
        if 'inherits' in raw_data:
            inherited_file = env.docker_template_path(f"config/{raw_data['inherits']}.yaml")
            with open(inherited_file, 'r') as stream:
                inherited_data = yaml.load(stream, Loader=yaml.FullLoader)
            raw_data = always_merger.merge(inherited_data, raw_data)
            self.file_path = [self.file_path, inherited_file]
        super().__init__(name, raw_data)

    def __str__(self):
        containers = '/n'.join(list(map(lambda c: str(c), self.containers.values())))
        return (f"{self.name}\n"
                f"{containers}")

    def _validate_required(self):
        self.required = self.try_get('required', [])
        for required in self.required:
            if not hasattr(self.service, required):
                raise Exception(f"service '{self.service.fullname}' does not contain required field '{required}'")
