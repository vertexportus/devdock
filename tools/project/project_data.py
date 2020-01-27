import functools

from .base_config import BaseConfig
from .project_config_data import ProjectConfigData
from .project_repo import ProjectRepo


class ProjectData(BaseConfig):
    master: ProjectConfigData
    repo: ProjectRepo
    path: str
    services: dict

    def __init__(self, name, master, data):
        super().__init__(name, data)
        self.master = master

    def __str__(self):
        services = functools.reduce(lambda a, b: f"{a}\n{b}", [f"   -- {k}: {v}" for k, v in self.services.items()])
        return f"project {self.name}\n  services:{len(self.services)}\n{services}"
