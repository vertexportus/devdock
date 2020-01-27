from ..base_config import BaseConfig
from .container_template_env import ContainerTemplateEnv
from .container_template_volumes import ContainerTemplateVolumes
from .container_template_image import ContainerTemplateImage
from .container_template_ports import ContainerTemplatePorts


class ContainerTemplateData(BaseConfig):
    fullname: str
    image: ContainerTemplateImage
    volumes: ContainerTemplateVolumes
    env: ContainerTemplateEnv
    ports: ContainerTemplatePorts
    depends_on: list

    def __init__(self, name, template, data):
        super().__init__(name, data)
        self.template = template

    def __str__(self):
        return (f"     (container:{self.name})\n"
                f"      - {self.image}"
                f"      - {self.volumes}"
                f"      - {self.env}"
                f"      - {self.ports}")
