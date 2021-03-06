import os
import re

import requests
import yaml
from clint.textui import progress

from project.generation import generate_build_files, rebuild_marker_append
from utils import env
from utils.templates import Templates
from utils.yaml_template_object import YamlTemplateObject


class ContainerTemplate(YamlTemplateObject):
    hidden_fields = ['service_template', 'service']
    yaml_tag = '!ContainerTemplate'
    name: str
    fullname: str
    tech_stack: list
    is_build: bool
    image: dict or str
    volumes_named: dict
    volumes_mapped: list
    env: dict
    ports: dict
    command: str
    download: dict
    depends_on: list or dict
    versioning: dict

    def __init__(self, name, service_template, templates: Templates, template_params, data):
        super().__init__(templates, template_params, data=data)
        self.service_template = service_template
        self.service = service_template.service
        self.name = name
        self._parse_tech_stack()
        self._parse_image()
        self._parse_volumes()
        self._parse_env()
        self._parse_ports()
        self._parse_command()
        self._parse_download()
        self._parse_depends_on()
        self._parse_versioning()

    def define_container_name(self):
        base_name = f"{self.service.project.name}_{self.service.name}" \
            if self.service.project and self.service.project.name != self.service.name else self.service.name
        self.fullname = f"{base_name}_{self.name}" if not self.service_template.is_single_container else base_name

    def post_load_init(self):
        pass
        # self._parse_env_imported()

    def final_load_env(self):
        self._parse_env()
        self._parse_env_imported()
        self._parse_env_from_service()

    def _parse_tech_stack(self):
        self.tech_stack = self.try_get('stack', [])
        if len(self.tech_stack) > 0:
            self.service.append_tech_stack(self.tech_stack)

    def get_env_var(self, env_name):
        env_prefix = self.service.env_prefix
        if env_name == 'host':
            return self.fullname
        env_full_name = f"{env_prefix}_{env_name}".upper()
        if env_name == 'port':
            return env_full_name
        if env_full_name in self.env:
            return env_full_name
        for port_config in self.ports.values():
            if port_config['env'] == env_full_name:
                return env.env_var_format(env_full_name, port_config['default'])
        return None

    def get_exported_env(self):
        env_prefix = self.service.env_prefix
        if 'env' in self._data:
            env_config = self._data['env']
            if 'exported' in env_config:
                return {f"{env_prefix}_{v}".upper(): self.get_env_var(v) for v in env_config['exported']}
            else:
                return {}
        else:
            return {}

    def _parse_image(self):
        if 'image' in self._data:
            if 'name' not in self._data['image']:
                raise Exception(f"required 'name' field on image config for container "
                                f"'{self.service_template.name}.{self.name}'")
            self.is_build = False
            self.image = f"{self._data['image']['name']}:{self._get_image_tag(self._data['image'])}"
        elif 'build' in self._data:
            build_config = self._data['build']
            self.is_build = True
            self.image = {
                'args': build_config['args'] if 'args' in build_config else {}
            }
            self.image['args']['TAG'] = self._get_image_tag(build_config)
        else:
            raise Exception(f"container needs either an 'image' or 'build' configs in "
                            f"'{self.service_template.name}.{self.name}'")

    def _get_image_tag(self, data):
        image_name = data['name']
        use_alpine = data['use_alpine'] if 'use_alpine' in data else True
        image_version = self.service.get_image_version(image_name)
        if image_version != 'latest':
            image_tag = (f"{image_version}"
                         f"{data['suffix'] if 'suffix' in data else ''}"
                         f"{'-alpine' if use_alpine else ''}")
        else:
            image_tag = f"{data['suffix'].replace('-','') if 'suffix' in data else ''}"
        if use_alpine and 'alpine' not in image_tag:
            image_tag = 'alpine' if image_tag == '' else f"{image_tag}-alpine"
        return image_tag if image_tag != '' else 'latest'

    def _parse_volumes(self):
        volumes = self._data['volumes'] if 'volumes' in self._data else {}
        self.volumes_named = volumes['named'] if 'named' in volumes else None
        self.volumes_mapped = list(map(lambda v: env.reverse_project_path(v), volumes['mapped'])) \
            if 'mapped' in volumes else None

    def _parse_env(self):
        if 'env' in self._data:
            env_config = self._data['env']
            env_prefix = self.service_template.service.env_prefix
            raw = {v: k for k, v in (env_config['raw'] if 'raw' in env_config else {}).items()}
            prefixed = {f"{env_prefix}_{v.upper()}": k for k, v in
                        (env_config['prefixed'] if 'prefixed' in env_config else {}).items()}
            self.env = {**raw, **prefixed}

    def _parse_env_imported(self):
        if 'env' in self._data:
            env_config = self._data['env']
            if 'import' in env_config:
                for to_import in env_config['import']:
                    if hasattr(self.service, to_import):
                        data = getattr(self.service, to_import);
                        if isinstance(data, list):
                            for d in data:
                                self._parse_env_imported_from_container(d)
                        else:
                            self._parse_env_imported_from_container(data)

    def _parse_env_imported_from_container(self, container_name):
        container = self.service.master.get_container_by_path(container_name)
        self.env = {**self.env, **{v: k for k, v in container.get_exported_env().items()}}

    def _parse_env_from_service(self):
        service_env_mapping = {}
        if isinstance(self.service.env, dict):
            service_env_mapping = {v.replace('$', ''): k for k, v in self.service.env.items()}
        else:
            for e in self.service.env:
                if '=' in e:
                    [k, v] = e.split('=')
                    service_env_mapping[v.replace('$', '')] = k
                else:
                    service_env_mapping[e] = e
        # save new env
        self.env = {**self.env, **service_env_mapping}

    def _parse_import_env(self, import_data):
        if '${' in import_data:  # do regex matching
            result = import_data
            matches = re.findall(r'\${(\w+\.\w+)}', import_data)
            for match in matches:
                result = result.replace(match, self._import_env(match)) \
                    if 'host' not in match \
                    else result.replace(f"${{{match}}}", self._import_env(match))
            return result
        else:  # direct import
            return self._import_env(import_data)

    def _import_env(self, import_path):
        [attr_name, env_name] = import_path.split('.')
        if not hasattr(self.service, attr_name):
            raise Exception(f"service {self.service.name} does not have attr '{attr_name}'")
        container = self.service.master.get_container_by_path(getattr(self.service, attr_name))
        return container.get_env_var(env_name)

    def _parse_ports(self):
        if 'ports' in self._data:
            self.ports = {}
            for port_name, port in self._data['ports'].items():
                env_prefix = self.service_template.service.env_prefix
                env_port_name = port_name.upper()
                if not env_port_name.startswith(env_prefix):
                    env_port_name = f"{env_prefix}_{env_port_name}_PORT"
                self.ports[port_name] = {
                    'default': port,
                    'env': env_port_name
                }

    def _parse_command(self):
        self.command = self.try_get('command', None)

    def _parse_download(self):
        self.download = self.try_get('download', None)

    def _parse_depends_on(self):
        self.depends_on = self.try_get('depends_on', None)

    def _parse_versioning(self):
        self.versioning = self.try_get('versioning', None)

    def generate_compose(self, compose_services, compose_volumes):
        compose = {}
        self._generate_compose_image(compose)
        self._generate_compose_volumes(compose, compose_volumes)
        self._generate_compose_env(compose)
        self._generate_compose_ports(compose)
        self._generate_compose_command(compose)
        self._generate_compose_depends_on(compose)
        compose_services[self.fullname] = compose

    def _generate_compose_image(self, compose):
        if self.is_build:
            path_suffix = f"/{self.name}" if not self.service_template.is_single_container else ""
            compose['build'] = {
                'context': (f"build/{self.service.master.current_env}/"
                            f"{self.service_template.name.replace('.', '/')}{path_suffix}"),
                'args': {k: self._generate_build_arg(v) for k, v in self.image['args'].items()},
            }
        else:
            compose['image'] = self.image

    def _generate_build_arg(self, arg):
        if type(arg) == str:
            return arg
        elif type(arg) == dict:
            if 'env' not in arg:
                raise Exception(f"env not in dict arg {self.service.name}:{self.name}")
            env_name = arg['env'].upper()
            if 'nested_prefix' in arg and arg['nested_prefix']:
                return env.env_var_nested_format(f"{self.service.env_prefix}_{env_name}", env_name, arg['default'])
            else:
                return env.env_var_format(env_name, arg['default'])
        return None

    def _generate_compose_volumes(self, compose, volumes):
        container_volumes = []
        if self.volumes_mapped:
            container_volumes += self.volumes_mapped
        if self.volumes_named:
            for volume_name, volume_dest in self.volumes_named.items():
                final_volume_name = f"{self.fullname}_{volume_name}"
                volumes[final_volume_name] = {'driver': 'local'}
                container_volumes.append(f"{final_volume_name}:{volume_dest}")
        if len(volumes) > 0:
            compose['volumes'] = container_volumes

    def _generate_compose_env(self, compose):
        envs = self.env.items() if hasattr(self, 'env') else []
        environment = {v: f"${{{k}}}" if k.isupper() else k for k, v in envs}
        if len(environment) > 0:
            compose['environment'] = environment
        if self.service.env_files:
            env_files = self.try_get('env.files', False)
            if env_files:
                if type(env_files) == bool:
                    files = [".env", f".{self.service.name}.env"]
                else:
                    files = env_files
                compose['env_file'] = [env.project_path(f) for f in files]

    def _generate_compose_ports(self, compose):
        if not hasattr(self, 'ports'):
            return
        ports = None
        service_ports_config = self.service_template.service.ports
        if type(service_ports_config) == bool:
            if service_ports_config:
                ports = []
                for port_name, port_config in self.ports.items():
                    ports.append(f"{env.env_var_format(port_config['env'], port_config['default'])}"
                                 f":{port_config['default']}")
        elif type(service_ports_config) == list:
            ports = []
            for port_name, port_config in self.ports.items():
                if port_name not in service_ports_config:
                    continue
                ports.append(f"{env.env_var_format(port_config['env'], port_config['default'])}"
                             f":{port_config['default']}")
        else:
            raise Exception(f"unsupported type on service.ports config for "
                            f"service {self.service_template.service.name}")
        if ports:
            compose['ports'] = ports

    def _generate_compose_command(self, compose):
        if self.command is not None:
            compose['command'] = self.command

    def _generate_compose_depends_on(self, compose):
        if self.depends_on:
            if type(self.depends_on) is dict:
                internal = self.depends_on['internal'] if 'internal' in self.depends_on else []
                external = [self._import_env(f"{v}.host") for v in
                            (self.depends_on['external'] if 'external' in self.depends_on else [])]
                compose['depends_on'] = internal + external
            else:
                compose['depends_on'] = self.depends_on

    def generate_build_files(self):
        template_params = {
            **self.service_template.params,
            'master': self.service.master,
            'project': self.service.project,
            'service': self.service,
            'siblings': self.service_template.containers
        }
        base_path = self.service_template.base_path
        path_suffix = f"/{self.name}" if not self.service_template.is_single_container else ""
        dest_path = (f"build/{self.service.master.current_env}/"
                     f"{base_path if type(base_path) == str else base_path[len(base_path) - 1]}{path_suffix}")
        paths = list(map(lambda x: f"{x}/build{path_suffix}", base_path if type(base_path) == list else [base_path]))
        changed = generate_build_files(paths, dest_path, self.templates, **template_params)
        # download files
        if self.download is not None:
            for download_path, download_url in self.download.items():
                if '/' in download_path:
                    download_base_path = env.docker_gen_path(f"{dest_path}/{'/'.join(download_path.split('/')[:-1])}")
                    if not os.path.exists(download_base_path):
                        os.mkdir(download_base_path)
                file_dest_path = env.docker_gen_path(f"{dest_path}/{download_path}")
                if not os.path.isfile(file_dest_path):
                    req = requests.get(download_url, stream=True)
                    with open(file_dest_path, 'wb') as f:
                        total_length = int(req.headers.get('content-length'))
                        for chunk in progress.bar(req.iter_content(chunk_size=1024),
                                                  label=f"downloading: {dest_path}/{download_path}  ",
                                                  expected_size=(total_length / 1024) + 1):
                            if chunk:
                                f.write(chunk)
                                f.flush()
                    changed = True
        if changed:
            rebuild_marker_append(self.get_proper_name())

    def get_proper_name(self):
        self_name = self.service.name
        names = [self.service.project.name] if self.service.project else []
        names.append(self.service.name)
        return '.'.join(names)
