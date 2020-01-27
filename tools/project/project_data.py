import functools

from .base_config import BaseConfig
from .project_config_data import ProjectConfigData
from .project_repo import ProjectRepo


class ProjectData(BaseConfig):
    master: ProjectConfigData
    repo: ProjectRepo
    path: str
    services: dict
    tech_stack: list

    def __init__(self, name, master, data):
        super().__init__(name, data)
        self.master = master
        self.tech_stack = []

    def __str__(self):
        services = functools.reduce(lambda a, b: f"{a}\n{b}", [f"   -- {k}: {v}" for k, v in self.services.items()])
        return f"project {self.name}\n  services:{len(self.services)}\n{services}"

    def append_to_tech_stack(self, tech):
        if type(tech) is str:
            self.tech_stack.append(tech)
        elif type(tech) is list:
            self.tech_stack += tech
        else:
            raise Exception(f"append_to_tech_stack(tech): type of '{tech}' (type:{type(tech)}) not supported")
