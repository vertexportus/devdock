from utils import env
from utils.templates import Templates
from utils.yaml_data_object import YamlDataObject
from .project import Project
from .project_repo import ProjectRepo
from .service import Service


class ProjectConfig(YamlDataObject):
    yaml_tag = '!ProjectConfig'
    hidden_fields = ['templates', 'defaults']
    defaults: dict
    templates: Templates
    docker: dict
    projects: dict
    services: dict
    devdock: ProjectRepo

    def __init__(self):
        super().__init__(file_path=env.project_config_file_path())
        self.defaults = self.load(env.devdock_path('docker/defaults.yaml'))
        self.templates = Templates(env.docker_template_path(), project_config=self)
        self.docker = self.try_get('docker', {})
        self.devdock = ProjectRepo(None, self.get_required('devdock'))
        self.projects = {k: Project(k, master=self, data=v) for k, v in self.try_get('projects', {}).items()}
        self.services = {k: Service(k, master=self, data=v) for k, v in self.try_get('services', {}).items()}
