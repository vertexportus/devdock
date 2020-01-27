from .container_template_data import ContainerTemplateData
from .container_template_env import ContainerTemplateEnv
from .container_template_image import ContainerTemplateImage
from .container_template_ports import ContainerTemplatePorts
from .container_template_volumes import ContainerTemplateVolumes


class ContainerTemplate(ContainerTemplateData):
    def __init__(self, name, template, data):
        super().__init__(name, template, data)
        self.fullname = self.template.service.fullname \
            if self.template.has_single_container else f"{self.template.service.fullname}_{name}"
        self.env = ContainerTemplateEnv(self, data=self.try_get('env', {}))
        self.image = ContainerTemplateImage(self, self._original_data)
        self.volumes = ContainerTemplateVolumes(self, data=self.try_get('volumes', {}))
        self.ports = ContainerTemplatePorts(self, data=self.try_get('ports', {}))

    def calculate_final_env(self):
        self.env.calculate_final_env()

    def update_dependencies(self):
        self.depends_on = list(map(lambda x: self.__get_sibling_fullname(x), self.try_get('depends_on', [])))
        self.depends_on += self.template.service.get_container_dependencies()

    def generate_compose(self, compose, for_env):
        service = {}
        self.image.generate_compose(service, for_env)
        self.volumes.generate_compose(service, compose['volumes'])
        self.env.generate_compose(service)
        self.ports.generate_compose(service)
        if len(self.depends_on) > 0:
            service['depends_on'] = self.depends_on
        compose['services'][self.fullname] = service

    def __get_sibling_fullname(self, container_name):
        if container_name in self.template.containers:
            return self.template.containers[container_name].fullname
        else:
            raise Exception(f"sibling container '{container_name}' not found in template '{self.template.name}'")
