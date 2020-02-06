import yaml
from jinja2 import Environment, FileSystemLoader, Template


class Templates:
    base_path: str
    env: Environment

    def __init__(self, base_path):
        self.base_path = base_path
        self.env = Environment(
            loader=FileSystemLoader(base_path),
            block_start_string='%{',
            block_end_string='}%',
            variable_start_string='%=',
            variable_end_string='=%',
            comment_start_string='%#',
            comment_end_string='#%'
        )

    def get_template(self, path) -> Template:
        return self.env.get_template(path)

    def render_template(self, path, **kwargs) -> str:
        return self.get_template(path).render(**kwargs)

    def render_template_yaml(self, path, **kwargs) -> dict:
        return yaml.load(
            self.render_template(path, **kwargs),
            Loader=yaml.FullLoader
        )
