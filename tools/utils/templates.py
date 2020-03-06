import yaml
from dict_deep import deep_get
from jinja2 import Environment, FileSystemLoader, Template


class Templates:
    base_path: str
    env: Environment

    def __init__(self, base_path, project_config):
        self.base_path = base_path
        self.project_config = project_config
        self.env = Environment(
            loader=FileSystemLoader(base_path),
            block_start_string='%{',
            block_end_string='}%',
            variable_start_string='%=',
            variable_end_string='=%',
            comment_start_string='%#',
            comment_end_string='#%'
        )
        self.env.filters['version'] = self.version
        self.env.filters['dmap'] = self.dmap
        self.env.filters['map_containers_fullname'] = self.map_containers_fullname

    def get_template(self, path) -> Template:
        return self.env.get_template(path)

    def render_template(self, path, **kwargs) -> str:
        return self.get_template(path).render(**kwargs)

    def render_template_yaml(self, path, **kwargs) -> dict:
        return yaml.load(
            self.render_template(path, **kwargs),
            Loader=yaml.FullLoader
        )

    def version(self, service, name) -> str:
        version = None
        if hasattr(service, 'version'):
            version_attr = service.version
            if version_attr:
                if type(version_attr) == str:
                    return version_attr
                elif name in version_attr:
                    version = version_attr[name]
        if not version:
            version = deep_get(self.project_config.defaults, f"{name}.version")
        return version

    @staticmethod
    def dmap(dictionary, fn) -> dict:
        return {k: fn(v) for k, v in dictionary.items()}

    @staticmethod
    def map_containers_fullname(containers, master):
        if type(containers) == dict:
            return {k: master.get_container_by_path(v).fullname for k, v in containers.items()}
        else:
            return list(map(lambda x: master.get_container_by_path(x).fullname, containers))

    def __deepcopy__(self, memodict=None):
        return {}
