from utils import env
from utils.yaml_data_object import YamlDataObject
from .project_repo import ProjectRepo
from .service import Service


class Project(YamlDataObject):
    hidden_fields = ['master']
    yaml_tag = '!Project'
    name: str
    repo: ProjectRepo
    path: str
    services: dict
    tech_stack: list

    def __init__(self, name, master, data):
        super().__init__(data=data)
        self.master = master
        self.name = name
        self.repo = ProjectRepo(self, data)
        self.path = env.project_path(name)
        self.tech_stack = []
        self.services = {k: Service(k, master=master, data=v, project=self)
                         for k, v in self.try_get('services', {}).items()}

    def define_container_names(self):
        for service in self.services.values():
            service.define_container_names()

    def post_load_init(self):
        for service in self.services.values():
            service.post_load_init()

    def generate_compose(self, compose_services, compose_volumes):
        for service in self.services.values():
            service.generate_compose(compose_services, compose_volumes)

    def get_service_by_tech(self, tech):
        return next(iter(filter(lambda x: tech in x.tech_stack, self.services.values())))

    def get_container_by_tech(self, tech):
        service = self.get_service_by_tech(tech)
        return service.get_container_by_tech(tech)

    def append_tech_stack(self, tech_stack):
        self.tech_stack += tech_stack
