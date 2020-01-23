import os
import re
import shutil
from pprint import pp

import yaml
from dict_deep import deep_get

from .project_config import ProjectConfig
from utils import env


class ProjectConfigManager:
    def __init__(self):
        self._config = ProjectConfig.load()
        # self._compose = None
        # with open(env.project_config_file_path(), 'r') as stream:
        #     self._config = yaml.load(stream, Loader=yaml.FullLoader)

    def get_projects(self):
        return self._config['projects']

    def get_services(self) -> dict:
        services = dict(self._config['services']) if 'services' in self._config else {}
        # add project-specific services to global services dict
        for project_name, project_config in self._config['projects'].items():
            if 'services' not in project_config:
                continue
            for project_service_name, project_service_config in project_config['services'].items():
                if project_service_name in services.keys():
                    project_service_name = f"{project_name}.{project_service_name}"
                project_service_config['project'] = {
                    'name': project_name,
                    'path': os.path.abspath(project_name)
                }
                services[project_service_name] = project_service_config
        return services

    def get_env(self, for_env=env.env()) -> dict:
        return
        envs = {}
        self._pre_generate_compose()
        self._calculate_dependencies()
        for service_name, service_config in self.get_services().items():
            envs[service_name] = []
            for container_service in service_config['gen'].values():
                envs[service_name] += container_service['envs']['all']
        return envs

    def generate_docker(self, for_env=env.env()):
        return
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
        self._pre_generate_compose()
        self._calculate_dependencies()
        # write docker-compose file
        self._write_compose_and_buildfiles(for_env)

    def _write_compose_and_buildfiles(self, for_env):
        for service_name, service_config in self.get_services().items():
            for container_name, container_config in service_config['gen'].items():
                self._compose['services'][container_name] = container_config['compose']
                self._generate_buildfiles(for_env, container_config['template'])
        with open(env.docker_compose_file_path(for_env), 'w') as docker_compose_file:
            yaml.dump(self._compose, docker_compose_file)

    @staticmethod
    def _calculate_container_name(service_name, template_name, service_config, are_named=False) -> str:
        prename = service_name
        if 'project' in service_config:
            prename = f"{service_config['project']['name']}_{service_name}"\
                if service_config['project']['name'] != service_name else service_name
        return f"{prename}_{template_name}" if are_named else prename

    def _pre_generate_compose(self):
        for service_name, service_config in self.get_services().items():
            self._pre_generate_compose_for_service(service_name, service_config)

    def _pre_generate_compose_for_service(self, name, config):
        template_config = self._load_template(config['template'])
        are_named = len(template_config) > 1
        for container_name, container_config in template_config.items():
            fullname = self._calculate_container_name(name, container_name, config, are_named)
            compose_config = {}
            # env
            environment = {}
            all_envs = []
            exported_envs = {}
            imported_envs = {}
            env_prefix = config['env_prefix'] if 'env_prefix' in config else fullname
            if 'env' in container_config:
                # prefixed envs
                if 'prefixed' in container_config['env']:
                    for env_name, env_var in container_config['env']['prefixed'].items():
                        env_final = f"{env_prefix}_{env_var}".upper()
                        environment[env_name] = env_final
                        all_envs.append(env_final)
                # exported envs
                if 'exported' in container_config['env']:
                    for exported_env in container_config['env']['exported']:
                        exported_envs[exported_env] = f"{env_prefix}_{exported_env}".upper()
                # imported envs
                if 'imported' in container_config['env']:
                    imported_envs = container_config['env']['imported']
            compose_config['environment'] = environment
            # image or dockerfile
            if 'image' in container_config:
                image = container_config['image']
                compose_config['image'] = f"{image['name']}:{config['tag'] if 'tag' in config else image['tag']}"
            elif 'build' in container_config:
                build_config = container_config['build']
                build = {'context': build_config['context']}
                if 'args' in build_config:
                    args = {}
                    for arg_name, arg_value in build_config['args'].items():
                        args[arg_name] = self._parse_var(arg_value, config)
                    build['args'] = args
                compose_config['build'] = build
            # volumes
            volumes = []
            if 'volumes' in container_config:
                # named volumes
                if 'named' in container_config['volumes']:
                    for volume_name, volume_path in container_config['volumes']['named'].items():
                        volume_fullname = f"{fullname}_{volume_name}"
                        volumes.append(f"{volume_fullname}:{volume_path}")
                        self._compose['volumes'][volume_fullname] = None
                # mapped volumes
                if 'mapped' in container_config['volumes']:
                    for mapped_volume in container_config['volumes']['mapped']:
                        [mapped_source, mapped_dest] = mapped_volume.split(':')
                        volumes.append(f"{self._parse_var(mapped_source, config)}:{mapped_dest}")
            compose_config['volumes'] = volumes
            # ports
            ports = []
            if 'ports' in container_config:
                if 'ports' in config and config['ports']:
                    for port_number, port_config in container_config['ports'].items():
                        if 'env' in port_config:
                            env_var = f"{env_prefix}_{port_config['env']}".upper()
                            all_envs.append(env_var)
                            port = f"${{{env_var}:-{port_number}}}:{port_number}"
                        else:
                            port = f"{port_number}:{port_number}"
                        ports.append(port)
                    compose_config['ports'] = ports
            # # save config
            if 'gen' not in config:
                config['gen'] = {}
            config['gen'][fullname] = {
                'template': config['template'],
                'compose': compose_config,
                'envs': {
                    'all': all_envs,
                    'exported': exported_envs,
                    'imported': imported_envs
                }
            }

    def _calculate_dependencies(self):
        for service_name, service_config in self.get_services().items():
            self._calculate_dependencies_for_service(service_name, service_config)

    def _calculate_dependencies_for_service(self, name, config):
        for container_name, container_config in config['gen'].items():
            exported_vars = {}
            depends_on = []
            # depends_on
            if 'depends_on' in config:
                if isinstance(config['depends_on'], str):
                    depends_on += self._get_container_list_for_service(config['depends_on'])
                else:
                    for depended_service_name in config['depends_on']:
                        depends_on += self._get_container_list_for_service(depended_service_name)
            # database
            if 'database' in config:
                depended_service = self._get_service_by_path(config['database'])
                exported_vars['database'] = {}
                for cname, cconf in depended_service['gen'].items():
                    exported_vars['database'] = {**exported_vars['database'], **cconf['envs']['exported']}
                depends_on += depended_service['gen'].keys()
            container_config['compose']['depends_on'] = depends_on
            # imported vars
            all_vars = container_config['envs']['all']
            environment = container_config['compose']['environment']
            for imported_var in container_config['envs']['imported'] if 'imported' in container_config['envs'] else []:
                var_name = deep_get(exported_vars, imported_var)
                if var_name:
                    all_vars.append(var_name)
                    environment[var_name] = var_name

    def _get_container_list_for_service(self, service_path) -> list:
        service = self._get_service_by_path(service_path)
        return service['gen'].keys()

    def _get_service_by_path(self, service_path) -> dict:
        # grab service
        service = None
        if '.' in service_path and 'projects' in self._config:
            [project_name, service_name] = service_path.split('.')
            service = deep_get(self._config['projects'], f"{project_name}.services.{service_name}")
        elif 'services' in self._config and service_path in self._config['services']:
            service = self._config['services'][service_path]
        if not service:
            raise Exception(f"No service found by '{service_path}'")
        # grab containers by template
        return service

    @staticmethod
    def _load_template(template_name) -> dict:
        template_file = env.docker_template_path(f"compose/{template_name}.yaml")
        with open(template_file, 'r') as stream:
            return yaml.load(stream, Loader=yaml.FullLoader)

    @classmethod
    def _generate_buildfiles(cls, for_env, template_name):
        build_path = f"{for_env}/{template_name.replace('.', '/')}"
        template_build_path = env.docker_template_path(f"build/{build_path}")
        gen_path = env.docker_gen_path(f"build/{build_path}")
        if os.path.isdir(template_build_path):
            if not os.path.exists(gen_path):
                os.makedirs(gen_path)
            for filename in os.listdir(template_build_path):
                orig_file_path = f"{template_build_path}/{filename}"
                dest_file_path = f"{gen_path}/{filename}"
                shutil.copyfile(orig_file_path, dest_file_path)
