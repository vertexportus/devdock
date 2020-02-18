from utils import env


class ContainerTemplateVolumes:
    named: dict
    mapped: list

    def __init__(self, container, data):
        self.container = container
        self.named = {
            f"{container.template.service.fullname}_{k}": v
            for k, v in (data['named'].items() if 'named' in data else {})}
        self.mapped = list(map(lambda v: env.reverse_project_path(v), data['mapped'] if 'mapped' in data else []))

    def __str__(self):
        return (f"volumes\n"
                f"         - named: {self.named if len(self.named) > 0 else '<none>'}\n"
                f"         - mapped: {self.mapped if len(self.mapped) > 0 else '<none>'}\n")

    def generate_compose(self, compose_service, compose_volumes):
        if len(self.named) == 0 and len(self.mapped) == 0:
            return
        if 'volumes' not in compose_service:
            compose_service['volumes'] = []
        for volume_name, named_volume_config in self.named.items():
            compose_service['volumes'].append(f"{volume_name}:{named_volume_config}")
            compose_volumes[volume_name] = None
        compose_service['volumes'] += self.mapped
