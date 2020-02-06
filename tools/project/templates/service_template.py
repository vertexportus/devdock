from .container_template import ContainerTemplate
from .service_template_data import ServiceTemplateData


class ServiceTemplate(ServiceTemplateData):
    def __init__(self, name, service):
        super().__init__(name, service)
        self._validate_required()
        self.has_single_container = len(self._original_data['containers']) < 2
        self.containers = {k: ContainerTemplate(k, self, v) for k, v in self._original_data['containers'].items()}

    def update_references(self):
        for container in self.containers.values():
            container.update_dependencies()
            container.calculate_final_env()

    def generate_compose(self, compose):
        for container in self.containers.values():
            container.generate_compose(compose)
