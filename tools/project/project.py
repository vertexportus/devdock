import functools
import os

from .project_data import ProjectData
from .project_repo import ProjectRepo
from .service import Service


class Project(ProjectData):
    def __init__(self, name, master, data):
        super().__init__(name, master, data)
        self.repo = ProjectRepo(self, data)
        self.path = os.path.abspath(name)
        self.services = {k: Service(k, master=self.master, project=self, data=v) for k, v in
                         data['services'].items()} if 'services' in data else {}
