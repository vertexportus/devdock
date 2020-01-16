import os
import re
import yaml
from dict_deep import deep_get
from utils import env


class ProjectConfigManager:
    def __init__(self):
        self._compose = {'version': '3', 'services': {}, 'volumes': {}}
        with open(env.project_config_file_path(), 'r') as stream:
            self._config = yaml.load(stream, Loader=yaml.FullLoader)

    def get_projects(self):
        return self._config['projects']

    def get_services(self):
        services = dict(self._config['services']) if 'services' in self._config else {}
        # add project-specific services to global services dict
        for project_name, project_config in self._config['projects'].items():
            for project_service_name, project_service_config in project_config['services'].items():
                if project_service_name in services:
                    raise Exception(f"project service named '{project_service_name}' already exists in global services")
                project_service_config['project'] = {
                    'path': os.path.abspath(project_name)
                }
                services[project_service_name] = project_service_config
        return services

    def generate_docker(self, for_env=env.env()):
        # get and mkdir gen path
        gen_path = env.docker_gen_path()
        if not os.path.isdir(gen_path):
            os.mkdir(gen_path)
        # generate config based on services
        for service_name, service_config in self.get_services().items():
            service_config['name'] = service_name
            template_name = service_config['template']
            template = self._load_compose_template(template_name, service_config)
            for template_service_name, template_service_config in template['services'].items():
                if 'ports' in service_config and service_config['ports']:
                    port_map_config = self._load_compose_template(f"port-mapping/{service_config['template']}",
                                                                  service_config)
                    template_service_config = {**template_service_config,
                                               **port_map_config['services'][template_service_name]}
                self._compose['services'][service_name] = template_service_config
                self._generate_build_templates(for_env, template_name, service_config)
            # append to volumes and generate build files
            if 'volumes' in template:
                self._compose['volumes'] = {**self._compose['volumes'], **template['volumes']}
        # write docker-compose file
        with open(env.docker_compose_file_path(for_env), 'w') as docker_compose_file:
            yaml.dump(self._compose, docker_compose_file)

    @classmethod
    def _load_compose_template(cls, template_name, service_config) -> dict:
        template_file = env.docker_template_path(f"compose/{template_name}.yaml")
        yaml_data = cls._load_parse_file(template_file, service_config)
        return yaml.load(yaml_data, Loader=yaml.FullLoader)

    @classmethod
    def _generate_build_templates(cls, for_env, template_name, service_config):
        build_path = f"{for_env}/{template_name.replace('.', '/')}"
        template_build_path = env.docker_template_path(f"build/{build_path}")
        gen_path = env.docker_gen_path(f"build/{build_path}")
        if os.path.isdir(template_build_path):
            for filename in os.listdir(template_build_path):
                file_data = cls._load_parse_file(f"{template_build_path}/{filename}", service_config)
                gen_file_path = f"{gen_path}/{filename}"
                if not os.path.exists(gen_file_path):
                    os.makedirs(os.path.dirname(gen_file_path))
                with open(gen_file_path, 'w') as stream:
                    stream.write(file_data)

    @staticmethod
    def _load_parse_file(file_path, config) -> str:
        if not os.path.isfile(file_path):
            raise Exception(f"file '{file_path}' does not exist")
        with open(file_path, 'r') as stream:
            file_data = stream.read()
        regex = re.compile(r"%\((.+)\)")
        for var in regex.findall(file_data):
            replace_var = f"%({var})"
            if ':' in var:
                [var, default_val] = var.split(':')
                if '=' in default_val:
                    [default_val, default_default] = default_val.split('=')
                    default_val = f"${{{default_val[1:]}:-{default_default}}}"
                value = deep_get(config, var)
                file_data = file_data.replace(replace_var, value if value else default_val)
            else:
                value = deep_get(config, var)
                file_data = file_data.replace(replace_var, value if value else '')
        return file_data
