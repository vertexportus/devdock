import functools
import os
import re

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
                return project.services[service_path] if service_path in project.services else None
            else:
                return None
        else:
            return self.services[service_path] if service_path in self.services else None

    def get_compose(self):
        compose = {'services': {}, 'volumes': {}}
        for service in self.services.values():
            service.generate_compose(compose)
        for project in self.projects.values():
            for project_service in project.services.values():
                project_service.generate_compose(compose)
        return compose


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


class Project(BaseConfig):
    master: ProjectConfig
    repo: str
    path: str
    services: dict

    def __init__(self, name, master, data):
        super().__init__(name, data)
        self.master = master
        self.repo = self.validate_get_field('repo')
        self.path = os.path.abspath(name)
        self.services = {k: Service(k, master=self.master, project=self, data=v) for k, v in
                         data['services'].items()} if 'services' in data else {}
        pass

    def __str__(self):
        services = functools.reduce(lambda a, b: f"{a}\n{b}", [f"   -- {k}: {v}" for k, v in self.services.items()])
        return f"project {self.name}\n  services:{len(self.services)}\n{services}"


class ServiceTemplateVolumes:
    named: dict
    mapped: list

    def __init__(self, template, data):
        self.template = template
        self.named = {
            f"{template.service.fullname}_{k}": v for k, v in (data['named'].items() if 'named' in data else {})}
        self.mapped = list(map(lambda v: template.service.parse_var(v),
                               data['mapped'] if 'mapped' in data else []))

    def __str__(self):
        return (f"volumes\n"
                f"         - named: {self.named if len(self.named) > 0 else '<none>'}\n"
                f"         - mapped: {self.mapped if len(self.mapped) > 0 else '<none>'}\n")


class ServiceTemplateEnv:
    prefix: str
    prefixed: dict
    exported: dict
    imported: dict
    environment: dict

    def __init__(self, template, data):
        self.template = template
        self.prefix = template.service.env_prefix.upper()
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
        service_path = getattr(self.template.service, attr)
        service = self.template.service.project.master.get_service_by_path(service_path)
        if not service:
            raise Exception(f"service '{service_path}' not found")
        exported_var = f"${{{service.template.env.exported[var]}}}" if var in service.template.env.exported else None
        if not exported_var:
            raise Exception(f"exported var '{dot_path}' not found")
        return exported_var

    def __str__(self):
        prefixed = f"         - prefixed: \n{self.__dict_to_str(self.prefixed)}\n" if len(self.prefixed) > 0 else ""
        exported = f"         - exported: \n{self.__dict_to_str(self.exported)}\n" if len(self.exported) > 0 else ""
        imported = f"         - imported: \n{self.__dict_to_str(self.imported)}\n" if len(self.imported) > 0 else ""
        environment = f"         - environment: \n{self.__dict_to_str(self.environment)}\n"\
            if len(self.environment) > 0 else ""
        return (f"env:\n"
                f"         - prefix: {self.prefix}\n{prefixed}{exported}{imported}{environment}")

    @classmethod
    def __dict_to_str(cls, d):
        return str.join('\n', list(map(cls.__env_map, {k: f"{k}={v}" for k, v in d.items()}.values())))

    @staticmethod
    def __env_map(e):
        return f"             {e}"


class ServiceTemplateImage:
    is_build: bool
    image: dict or str

    def __init__(self, template, data):
        self.template = template
        if 'image' in data:
            self.__as_image(data['image'])
        elif 'build' in data:
            self.__as_build(data['build'])
        else:
            raise Exception(f"No build or image config set on template {template.name}")

    def __str__(self):
        return (f"image(build:{self.is_build}):\n"
                f"         - {self.image if type(self.image) is str else self.__dict_to_str(self.image)}\n")

    @classmethod
    def __dict_to_str(cls, d):
        return str.join('\n         - ', list(map(lambda e: f"{e}", {k: f"{k}={v}" for k, v in d.items()}.values())))

    def __as_image(self, image):
        self.is_build = False
        self.image = f"{image['name']}:{self.template.service.parse_var(image['tag'])}"
        pass

    def __as_build(self, build):
        self.is_build = True
        self.image = self.__process_vars(build)
        pass

    def __process_vars(self, value):
        if type(value) is str:
            return self.template.service.parse_var(value)
        elif type(value) is dict:
            return {k: self.__process_vars(v) for k, v in value.items()}
        else:
            raise Exception(f"invalid data type in template '{self.template.name}'")


class ServiceTemplatePorts:
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
        ports = str.join('\n         - ', list(map(lambda e: f"  {e}", {k: f"{k}={v}" for k, v in self.mapping.items()}.values())))
        return f"ports:\n        {ports}"


class ContainerTemplate(BaseConfig):
    image: ServiceTemplateImage
    volumes: ServiceTemplateVolumes
    env: ServiceTemplateEnv
    ports: ServiceTemplatePorts

    def __init(self, name, template, service, data):
        super().__init__(name, data)
        self.template = template
        self.service = service
        self.env = ServiceTemplateEnv(self, data=self.try_get('env', {}))
        self.image = ServiceTemplateImage(self, self._original_data)
        self.volumes = ServiceTemplateVolumes(self, data=self.try_get('volumes', {}))
        self.ports = ServiceTemplatePorts(self, data=self.try_get('ports', {}))

    def __str__(self):
        return (f"      - {self.image}"
                f"      - {self.volumes}"
                f"      - {self.env}"
                f"      - {self.ports}")


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

    def calculate_final_env(self):
        for container in self.containers:
            container.env.calculate_final_env()

    def __str__(self):
        return (f"{self.name}\n"
                f"{self.containers}")

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
    tag: str
    env_prefix: str

    def __init__(self, name, master, project, data):
        super().__init__(name, data)
        self.fullname = name
        self.master = master
        self.project = project
        self.env_prefix = self.try_get('env_prefix', self.fullname)
        self.database = self.try_get('database', None)
        self.tag = self.try_get('tag', None)
        self.template = ServiceTemplate(data['template'], self)

    def __str__(self):
        return f"service {self.name} ({self.fullname})\n    template: {self.template}"

    def generate_compose(self, compose):
        pass

    def parse_var(self, var):
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
