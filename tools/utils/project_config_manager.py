import os
import re
import yaml
from dict_deep import deep_get
from utils import env


class ProjectConfigManager:
    def __init__(self):
        self._compose = {'version': '3', 'services': {}, 'volumes': {}}
        with open(env.project_config_path(), 'r') as stream:
            self._config = yaml.load(stream, Loader=yaml.FullLoader)

    def update(self, for_env=None):
        for service_name, service_config in self._config['services'].items():
            service_config['name'] = service_name
            template = self._load_template(service_config['template'], service_config)
            for template_name, template_config in template['services'].items():
                if 'ports' in service_config and service_config['ports']:
                    port_map_config = self._load_template(f"port-mapping/{service_config['template']}", service_config)
                    template_config = {**template_config, **port_map_config['services'][template_name]}
                self._compose['services'][service_name] = template_config
            self._compose['volumes'] = {**self._compose['volumes'], **template['volumes']}
        with open(env.project_path(f"devdock/docker/gen/docker-compose-{for_env if for_env else env.env()}.yaml"), 'w')\
                as docker_compose_file:
            yaml.dump(self._compose, docker_compose_file)

    @staticmethod
    def _load_template(template_name, service_config) -> dict:
        regex = re.compile(r"%\((.+)\)")
        with open(env.project_path(f"devdock/docker/templates/{template_name}.yaml"), 'r') as stream:
            yaml_data = stream.read()
        for var in regex.findall(yaml_data):
            replace_var = f"%({var})"
            if ':' in var:
                [var, default_val] = var.split(':')
                if '=' in default_val:
                    [default_val, default_default] = default_val.split('=')
                    default_val = f"${{{default_val[1:]}:-{default_default}}}"
                value = deep_get(service_config, var)
                yaml_data = yaml_data.replace(replace_var, value if value else default_val)
            else:
                value = deep_get(service_config, var)
                yaml_data = yaml_data.replace(replace_var, value if value else '')
        return yaml.load(yaml_data, Loader=yaml.FullLoader)
