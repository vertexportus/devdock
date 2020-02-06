from pprint import pp

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
        self.file_path = f"config/{name}.yaml"
        template_params = {
            'env': env.get_env_dict(),
            'service': service,
            'project': service.project,
            'defaults': service.master.defaults
        }
        raw_data = service.master.templates.render_template_yaml(self.file_path, **template_params)
        if 'inherits' in raw_data:
            inherited_file = f"config/{raw_data['inherits']}.yaml"
            inherited_data = service.master.templates.render_template_yaml(inherited_file, **template_params)
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
            if not self.service.data_hasattr(required):
                raise Exception(f"service '{self.service.fullname}' does not contain required field '{required}'")
