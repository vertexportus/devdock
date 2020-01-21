import os
import re
from pprint import pp

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

    def get_services(self) -> dict:
        services = dict(self._config['services']) if 'services' in self._config else {}
        # add project-specific services to global services dict
        for project_name, project_config in self._config['projects'].items():
            if 'services' not in project_config:
                continue
            for project_service_name, project_service_config in project_config['services'].items():
                project_service_config['project'] = {
                    'name': project_name,
                    'path': os.path.abspath(project_name)
                }
                services[project_service_name] = project_service_config
        return services

    def get_env(self, for_env=env.env()) -> dict:
        envs = {}
        if len(self._compose['services']) == 0:
            with open(env.docker_compose_file_path(for_env), 'r') as docker_compose_file:
                self._compose = yaml.load(docker_compose_file, Loader=yaml.FullLoader)
        for service_name, service_config in self._compose['services'].items():
            service_envs = []
            if 'environment' in service_config:
                for env_dest, env_orig in service_config['environment'].items():
                    service_envs.append(env_orig)
            envs[service_name] = service_envs
        return envs

    def generate_docker(self, for_env=env.env()):
        # get and mkdir gen path
        self._compose = {
            'version': '3',
            'services': {},
            'volumes': {}
        }
        gen_path = env.docker_gen_path()
        if not os.path.isdir(gen_path):
            os.mkdir(gen_path)
        # generate config based on services
        for service_name, service_config in self.get_services().items():
            self._generate_compose_for_service(service_name, service_config)
        # write docker-compose file
        with open(env.docker_compose_file_path(for_env), 'w') as docker_compose_file:
            yaml.dump(self._compose, docker_compose_file)

    def _generate_compose_for_service(self, name, config):
        template_config = self._load_template(config['template'])
        are_named = len(template_config) > 1
        for service_name, service_config in template_config.items():
            fullname = f"{name}_{service_name}" if are_named else name
            final_config = {}
            # env
            environment = {}
            env_prefix = config['env_prefix'] if 'env_prefix' in config else fullname.upper()
            if 'env' in service_config:
                # prefixed envs
                if 'prefixed' in service_config['env']:
                    for env_name, env_var in service_config['env']['prefixed'].items():
                        environment[env_name] = f"{env_prefix}_{env_var}"
            final_config['environment'] = environment
            # image or dockerfile
            if 'image' in service_config:
                image = service_config['image']
                final_config['image'] = f"{image['name']}:{config['tag'] if 'tag' in config else image['tag']}"
            elif 'build' in service_config:
                build_config = service_config['build']
                build = {'context': build_config['context']}
                if 'args' in build_config:
                    args = {}
                    for arg_name, arg_value in build_config['args'].items():
                        args[arg_name] = self._parse_var(arg_value, config)
                    build['args'] = args
                final_config['build'] = build
            # volumes
            volumes = []
            if 'volumes' in service_config:
                # named volumes
                if 'named' in service_config['volumes']:
                    for volume_name, volume_path in service_config['volumes']['named'].items():
                        volume_fullname = f"{fullname}_{volume_name}"
                        volumes.append(f"{volume_fullname}:{volume_path}")
                        self._compose['volumes'][volume_fullname] = None
                # mapped volumes
                if 'mapped' in service_config['volumes']:
                    for mapped_volume in service_config['volumes']['mapped']:
                        [mapped_source, mapped_dest] = mapped_volume.split(':')
                        volumes.append(f"{self._parse_var(mapped_source, config)}:{mapped_dest}")
            final_config['volumes'] = volumes
            # ports
            ports = []
            if 'ports' in service_config:
                if 'ports' in config and config['ports']:
                    for port_number, port_config in service_config['ports'].items():
                        if 'env' in port_config:
                            env_var = f"{env_prefix}_{port_config['env']}"
                            final_config['environment'][env_var] = env_var
                            port = f"${{{env_var}:-{port_number}}}:{port_number}"
                        else:
                            port = f"{port_number}:{port_number}"
                        ports.append(port)
                    final_config['ports'] = ports
            # # save config
            self._compose['services'][fullname] = final_config

    @staticmethod
    def _load_template(template_name) -> dict:
        template_file = env.docker_template_path(f"compose/{template_name}.yaml")
        with open(template_file, 'r') as stream:
            return yaml.load(stream, Loader=yaml.FullLoader)

    @staticmethod
    def _parse_var(var, config):
        # if its a variable
        if '%(' in var:
            regex = re.compile(r"%\((.+)\)")
            result = regex.findall(var)
            # if regex found variable dot path
            if len(result) > 0:
                default_val = None
                dot_path = result[0]
                # take care to allow for default values
                if ':' in dot_path:
                    [dot_path, default_val] = dot_path.split(':')
                val = deep_get(config, dot_path)
                if not val:
                    if not default_val:
                        raise Exception(f"{dot_path} not found in service config")
                    else:
                        return default_val
                else:
                    return val
            # regex found no variable
            else:
                return var
        # its not a variable
        else:
            return var

    @classmethod
    def _load_compose_template(cls, template_name, service_config) -> dict:
        result = {'services': {}}
        template_file = env.docker_template_path(f"compose/{template_name}.yaml")
        yaml_data = cls._load_parse_file(template_file, service_config)
        template = yaml.load(yaml_data, Loader=yaml.FullLoader)
        return result

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
