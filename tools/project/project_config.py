import functools
import os
import re
import shutil
from pprint import pp

import yaml

from utils import env


class ProjectConfig:
    projects: dict
    services: dict

    @classmethod
    def load(cls):
        with open(env.project_config_file_path(), 'r') as stream:
            return cls(yaml.load(stream, Loader=yaml.FullLoader))

    def __init__(self, data):
        self.projects = {k: Project(k, master=self, data=v) for k, v in data['projects'].items()}
        self.services = {k: Service(k, master=self, project=None, data=v) for k, v in
                         data['services'].items()} if 'services' in data else {}
        for service in self.services.values():
            service.update_references()
        for project in self.projects.values():
            for project_service in project.services.values():
                project_service.update_references()

    def __str__(self):
        projects = functools.reduce(lambda a, b: f"{a}\n{b}", [f" -- {k}: {v}" for k, v in self.projects.items()])
        services = functools.reduce(lambda a, b: f"{a}\n{b}", [f" -- {k}: {v}" for k, v in self.services.items()])
        return (f"projects: {len(self.projects)}\n{projects}"
                f"\n\nservices: {len(self.services)}\n{services}")

    def get_service_by_path(self, service_path):
        if '.' in service_path:
            [project_name, service_name] = service_path.split('.')
            if project_name in self.projects:
                project = self.projects[project_name]
                return project.services[service_name] if service_name in project.services else None
            else:
                return None
        else:
            return self.services[service_path] if service_path in self.services else None

    def get_compose(self, for_env):
        compose = {'services': {}, 'volumes': {}}
        for service in self.services.values():
            service.generate_compose(compose, for_env)
        for project in self.projects.values():
            for project_service in project.services.values():
                project_service.generate_compose(compose, for_env)
        return compose

    def get_env(self):
        envs = []
        for service in self.services.values():
            envs += service.get_env()
        for project in self.projects.values():
            for project_service in project.services.values():
                envs += project_service.get_env()
        return list(dict.fromkeys(envs))


class BaseConfig:
    name: str
    _class_type: str
    _original_data: dict

    def __init__(self, name, original_data):
        self.name = name
        self._class_type = type(self).__name__
        self._original_data = original_data

    def validate_get_field(self, field):
        if field not in self._original_data:
            raise Exception(f"validation error: {field} is required in {self._class_type} config {self.name}")
        return self._original_data[field]

    def try_get(self, field, default):
        return self._original_data[field] if field in self._original_data else default


class ProjectRepo:
    base_urls = {
        'github': {'ssh': 'git@github.com:', 'http': 'https://github.com/'}
    }
    url: str

    def __init__(self, project, data):
        if 'github' in data:
            self._set_url('github', data['github'])
        elif 'repo' in data:
            self._set_url('repo', data['repo'])
        else:
            raise Exception(f"No repository configured on project {project.name}")

    def _set_url(self, url_type, url):
        self.url = f"{self.base_urls[url_type]['ssh' if env.git_use_ssh() else 'http']}{url}"\
            if url_type in self.base_urls else url


class Project(BaseConfig):
    master: ProjectConfig
    repo: ProjectRepo
    path: str
    services: dict

    def __init__(self, name, master, data):
        super().__init__(name, data)
        self.master = master
        self.repo = ProjectRepo(self, data)
        self.path = os.path.abspath(name)
        self.services = {k: Service(k, master=self.master, project=self, data=v) for k, v in
                         data['services'].items()} if 'services' in data else {}
        pass

    def __str__(self):
        services = functools.reduce(lambda a, b: f"{a}\n{b}", [f"   -- {k}: {v}" for k, v in self.services.items()])
        return f"project {self.name}\n  services:{len(self.services)}\n{services}"


class ContainerTemplateVolumes:
    named: dict
    mapped: list

    def __init__(self, container, data):
        self.container = container
        self.named = {
            f"{container.template.service.fullname}_{k}": v
            for k, v in (data['named'].items() if 'named' in data else {})}
        self.mapped = list(map(lambda v: env.reverse_project_path(container.template.service.parse_var(v)),
                               data['mapped'] if 'mapped' in data else []))

    def __str__(self):
        return (f"volumes\n"
                f"         - named: {self.named if len(self.named) > 0 else '<none>'}\n"
                f"         - mapped: {self.mapped if len(self.mapped) > 0 else '<none>'}\n")

    def generate_compose(self, compose_service, compose_volumes):
        if len(self.named) == 0 and len(self.mapped) == 0:
            return
        if 'volumes' not in compose_service:
            compose_service['volumes'] = []
        for volume_name, named_volume_config in self.named.items():
            compose_service['volumes'].append(f"{volume_name}:{named_volume_config}")
            compose_volumes[volume_name] = None
        compose_service['volumes'] += self.mapped


class ContainerTemplateEnv:
    prefix: str
    prefixed: dict
    exported: dict
    imported: dict
    environment: dict

    def __init__(self, container, data):
        self.container = container
        self.prefix = container.template.service.env_prefix.upper()
        self.prefixed = {k: f"{self.prefix}_{v.upper()}"
                         for k, v in (data['prefixed'] if 'prefixed' in data else {}).items()}
        exported_raw = (data['exported'] if 'exported' in data else []) + ['host']
        self.exported = dict(zip(exported_raw, list(map(lambda e: f"{self.prefix}_{e.upper()}", exported_raw))))
        self.imported = data['imported'] if 'imported' in data else {}
        self.environment = {}

    def calculate_final_env(self):
        # calculate imported
        prefixed = {k: f"${{{v}}}" for k, v in self.prefixed.items()}
        imported = {k: self.import_env(v) for k, v in self.imported.items()}
        self.environment = {**prefixed, **imported}

    def import_env(self, dot_path):
        [attr, var] = dot_path.split('.')
        service_path = getattr(self.container.template.service, attr)
        service = self.container.template.service.project.master.get_service_by_path(service_path)
        if not service:
            raise Exception(f"service '{service_path}' not found")
        exported_var = None
        for container in service.template.containers:
            if var in container.env.exported:
                exported_var = f"${{{container.env.exported[var]}}}"
                break
        if not exported_var:
            raise Exception(f"exported var '{dot_path}' not found")
        return exported_var

    def __str__(self):
        prefixed = f"         - prefixed: \n{self.__dict_to_str(self.prefixed)}\n" if len(self.prefixed) > 0 else ""
        exported = f"         - exported: \n{self.__dict_to_str(self.exported)}\n" if len(self.exported) > 0 else ""
        imported = f"         - imported: \n{self.__dict_to_str(self.imported)}\n" if len(self.imported) > 0 else ""
        environment = f"         - environment: \n{self.__dict_to_str(self.environment)}\n" \
            if len(self.environment) > 0 else ""
        return (f"env:\n"
                f"         - prefix: {self.prefix}\n{prefixed}{exported}{imported}{environment}")

    def generate_compose(self, compose_service):
        compose_service['environment'] = {**self.environment}

    @classmethod
    def __dict_to_str(cls, d):
        return str.join('\n', list(map(cls.__env_map, {k: f"{k}={v}" for k, v in d.items()}.values())))

    @staticmethod
    def __env_map(e):
        return f"             {e}"


class ContainerTemplateImage:
    is_build: bool
    image: dict or str

    def __init__(self, container, data):
        self.container = container
        if 'image' in data:
            self.__as_image(data['image'])
        elif 'build' in data:
            self.__as_build(data['build'])
        else:
            raise Exception(f"No build or image config set on template '{container.name}'")

    def __str__(self):
        return (f"image(build:{self.is_build}):\n"
                f"         - {self.image if type(self.image) is str else self.__dict_to_str(self.image)}\n")

    def generate_compose(self, compose_service, for_env):
        if self.is_build:
            self.image['context'] = re.sub(r"\${*ENV}*", for_env, self.image['context'])
            compose_service['build'] = {**self.image}
            build_orig_path = env.docker_template_path(self.image['context'])
            build_dest_path = env.docker_gen_path(self.image['context'])
            if os.path.isdir(build_dest_path):
                shutil.rmtree(build_dest_path)
            shutil.copytree(build_orig_path, build_dest_path)
        else:
            compose_service['image'] = self.image

    @classmethod
    def __dict_to_str(cls, d):
        return str.join('\n         - ', list(map(lambda e: f"{e}", {k: f"{k}={v}" for k, v in d.items()}.values())))

    def __as_image(self, image):
        self.is_build = False
        self.image = f"{image['name']}:{self.container.template.service.parse_var(image['tag'])}"
        pass

    def __as_build(self, build):
        self.is_build = True
        self.image = self.__process_vars(build)
        pass

    def __process_vars(self, value):
        if type(value) is str:
            return self.container.template.service.parse_var(value)
        elif type(value) is dict:
            return {k: self.__process_vars(v) for k, v in value.items()}
        else:
            raise Exception(f"invalid data type in template '{self.container.template.name}'")


class ContainerTemplatePorts:
    mapping: dict

    def __init__(self, template, data):
        self.template = template
        self.mapping = {}
        for port_number in data:
            port_config = data[port_number]
            if port_config and 'env' in port_config:
                self.mapping[port_number] = template.env.exported[port_config['env']]
            else:
                self.mapping[port_number] = port_number
        pass

    def __str__(self):
        ports = str.join('\n         - ',
                         list(map(lambda e: f"  {e}", {k: f"{k}={v}" for k, v in self.mapping.items()}.values())))
        return f"ports:\n        {ports}"

    def generate_compose(self, compose_service):
        compose_service['ports'] = list({k: f"${{{v}:-{k}}}:{k}" for k, v in self.mapping.items()}.values())


class ContainerTemplate(BaseConfig):
    image: ContainerTemplateImage
    volumes: ContainerTemplateVolumes
    env: ContainerTemplateEnv
    ports: ContainerTemplatePorts

    def __init__(self, name, template, data):
        super().__init__(name, data)
        self.template = template
        self.env = ContainerTemplateEnv(self, data=self.try_get('env', {}))
        self.image = ContainerTemplateImage(self, self._original_data)
        self.volumes = ContainerTemplateVolumes(self, data=self.try_get('volumes', {}))
        self.ports = ContainerTemplatePorts(self, data=self.try_get('ports', {}))

    def __str__(self):
        return (f"     (container:{self.name})\n"
                f"      - {self.image}"
                f"      - {self.volumes}"
                f"      - {self.env}"
                f"      - {self.ports}")

    def generate_compose(self, container_name, compose, for_env):
        service = {}
        self.image.generate_compose(service, for_env)
        self.volumes.generate_compose(service, compose['volumes'])
        self.env.generate_compose(service)
        self.ports.generate_compose(service)
        compose['services'][container_name] = service


class ServiceTemplate(BaseConfig):
    file_path: str
    required: list
    containers: list

    def __init__(self, name, service):
        self.service = service
        self.file_path = env.docker_template_path(f"compose/{name}.yaml")
        with open(self.file_path, 'r') as stream:
            raw_data = yaml.load(stream, Loader=yaml.FullLoader)
        super().__init__(name, raw_data)
        self._validate_required()
        self.containers = []
        for container_template_name, container_config in raw_data['containers'].items():
            self.containers.append(ContainerTemplate(container_template_name, self, container_config))

    def calculate_final_env(self):
        for container in self.containers:
            container.env.calculate_final_env()

    def generate_compose(self, compose, for_env):
        num_containers = len(self.containers)
        for container in self.containers:
            container_name = self.service.fullname if num_containers < 2 else f"{self.service.fullname}_{container.name}"
            container.generate_compose(container_name, compose, for_env)

    def __str__(self):
        containers = '/n'.join(list(map(lambda c: str(c), self.containers)))
        return (f"{self.name}\n"
                f"{containers}")

    def _validate_required(self):
        self.required = self.try_get('required', [])
        for required in self.required:
            if not hasattr(self.service, required):
                raise Exception(f"service '{self.service.fullname}' does not contain required field '{required}'")


class Service(BaseConfig):
    fullname: str
    master: ProjectConfig
    project: Project
    template: ServiceTemplate
    database: str
    version: str or dict
    env_prefix: str

    def __init__(self, name, master, project, data):
        super().__init__(name, data)
        self.fullname = name
        self.master = master
        self.project = project
        self.env_prefix = self.try_get('env_prefix', self.fullname)
        self.database = self.try_get('database', None)
        self.version = self.try_get('version', None)
        self.template = ServiceTemplate(data['template'], self)

    def __str__(self):
        return f"service {self.name} ({self.fullname})\n    template: {self.template}"

    def generate_compose(self, compose, for_env):
        self.template.generate_compose(compose, for_env)

    def get_env(self) -> list:
        envs = []
        r = re.compile(r"\${*([A-Z_]+)}*")
        for container in self.template.containers:
            envs += list(map(lambda e: r.findall(e)[0], container.env.environment.values()))
        return envs

    def parse_var(self, var) -> str:
        # if its a variable
        if '%(' in var:
            regex = re.compile(r"%\((.+)\)")
            result = regex.findall(var)
            # if regex found variable dot path
            if len(result) > 0:
                default_val = None
                raw_var = result[0]
                # take care to allow for default values
                if ':' in raw_var:
                    [dot_path, default_val] = raw_var.split(':')
                else:
                    dot_path = raw_var
                # take care to allow for method transforms
                if '!' in dot_path:
                    [dot_path, func] = dot_path.split('!')
                else:
                    func = None
                # get value
                dot_path_split = dot_path.split('.')
                obj = self
                for attr_name in dot_path_split:
                    if attr_name == 'service':
                        obj = self
                    elif hasattr(obj, attr_name):
                        obj = getattr(obj, attr_name)
                    else:
                        obj = None
                        break
                val = obj
                # run transform function if requested
                if func and hasattr(val, func):
                    val = getattr(val, func)()

                if not val:
                    if not default_val:
                        raise Exception(f"'{dot_path}' not found in config")
                    else:
                        return var.replace(f"%({raw_var})", default_val)
                else:
                    return var.replace(f"%({raw_var})", str(val))

            # regex found no variable
            else:
                return var
        # its not a variable
        else:
            return var

    def update_references(self):
        self.template.calculate_final_env()
