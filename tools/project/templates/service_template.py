from dict_deep import deep_get

from .container_template import ContainerTemplate
from .service_template_data import ServiceTemplateData


class ServiceTemplate(ServiceTemplateData):
    def __init__(self, name, service):
        super().__init__(name, service)
        self._validate_required()
        self.containers = {k: ContainerTemplate(k, self, v) for k, v in self._original_data['containers'].items()}

    def update_references(self):
        references = {}
        reference_maps = self.try_get('references', [])
        for ref in reference_maps:
            [origin, dest] = ref.split(':')
            values = deep_get(self.template_params, origin)
            if not values:
                raise Exception(f"references trying to get data '{origin}' that is invalid")
            [container_name, prop] = dest.split('.', 1)
            references[container_name] = {
                'prop': prop,
                'values': {k: self.service.master.get_container_name_by_path(v) for k, v in values.items()}
            }
        for container in self.containers.values():
            container.update_dependencies(references[container.name] if container.name in references else None)
            container.calculate_final_env()

    def generate_compose(self, compose):
        for container in self.containers.values():
            container.generate_compose(compose)
