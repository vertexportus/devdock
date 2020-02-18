from utils import env
from .project_data import ProjectData
from .project_repo import ProjectRepo
from .service import Service


class Project(ProjectData):
    def __init__(self, name, master, data):
        super().__init__(name, master, data)
        self.repo = ProjectRepo(self, data)
        self.path = env.project_path(name)
        self.services = {k: Service(k, master=self.master, project=self, data=v) for k, v in
                         data['services'].items()} if 'services' in data else {}

    def get_container_by_stack(self, stack: str):
        service = next(iter(filter(lambda x: stack in x.tech_stack, self.services.values())))
        if service:
            return next(iter(filter(lambda x: stack in x.tech_stack, service.template.containers.values())))
        return None
