import re

from .base_config import BaseConfig
from .project_config_data import ProjectConfigData
from .project_data import ProjectData
from .templates.service_template import ServiceTemplate


class ServiceData(BaseConfig):
    fullname: str
    master: ProjectConfigData
    project: ProjectData
    template: ServiceTemplate
    database: str
    version: str or dict
    ports: bool or list
    env_prefix: str
    env_files: bool or list
    tech_stack: list

    @property
    def containers(self):
        return self.template.containers

    def __init__(self, name, master, project, data):
        super().__init__(name, data)
        self.fullname = name
        self.master = master
        self.project = project
        self.tech_stack = []

    def __str__(self):
        return f"service {self.name} ({self.fullname})\n    template: {self.template}"

    def append_to_tech_stack(self, stack):
        self.tech_stack += stack
        if self.project and len(self.tech_stack) > 0:
            self.project.append_to_tech_stack(stack)

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
