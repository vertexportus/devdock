import yaml

from utils import env
from ..base_config import BaseConfig


class ServiceTemplateData(BaseConfig):
    file_path: str
    required: list
    containers: dict
    has_single_container: bool

    def __init__(self, name, service):
        self.service = service
        self.file_path = env.docker_template_path(f"compose/{name}.yaml")
        with open(self.file_path, 'r') as stream:
            raw_data = yaml.load(stream, Loader=yaml.FullLoader)
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
