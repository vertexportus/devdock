import functools

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
        print(self)

    def __str__(self):
        projects = functools.reduce(lambda a, b: f"{a}\n{b}", [f" -- {k}: {v}" for k, v in self.projects.items()])
        services = functools.reduce(lambda a, b: f"{a}\n{b}", [f" -- {k}: {v}" for k, v in self.services.items()])
        return (f"projects: {len(self.projects)}\n{projects}"
                f"\n\nservices: {len(self.services)}\n{services}")


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


class Project(BaseConfig):
    master: ProjectConfig
    repo: str
    services: dict

    def __init__(self, name, master, data):
        super().__init__(name, data)
        self.master = master
        self.repo = self.validate_get_field('repo')
        self.services = {k: Service(k, master=self.master, project=self, data=v) for k, v in
                         data['services'].items()} if 'services' in data else {}
        pass

    def __str__(self):
        services = functools.reduce(lambda a, b: f"{a}\n{b}", [f"   -- {k}: {v}" for k, v in self.services.items()])
        return f"project {self.name}\n  services:{len(self.services)}\n{services}"


class ServiceTemplateVolumes:
    def __init__(self):
        pass


class ServiceTemplate(BaseConfig):
    file_path: str
    service_name: str
    required: list

    def __init__(self, name, service_name):
        self.file_path = env.docker_template_path(f"compose/{name}.yaml")
        with open(self.file_path, 'r') as stream:
            raw_data = yaml.load(stream, Loader=yaml.FullLoader)
        super().__init__(name, raw_data[name.replace('.', '_')])
        self.service_name = service_name
        self.required = self._original_data['required'] if 'required' in self._original_data else []

    def __str__(self):
        return f"{self.name}\n      - {self._original_data}"


class Service(BaseConfig):
    fullname: str
    master: ProjectConfig
    project: Project
    template: ServiceTemplate

    def __init__(self, name, master, project, data):
        super().__init__(name, data)
        self.fullname = name
        self.master = master
        self.project = project
        self.template = ServiceTemplate(data['template'], self.fullname)

    def __str__(self):
        return f"service {self.name} ({self.fullname})\n    template: {self.template}"
