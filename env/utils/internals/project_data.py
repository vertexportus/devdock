import os
import yaml


def load_project():
    project_file = f"{os.environ['PROJECT_PATH']}/project.yaml"
    with open(project_file, 'r') as stream:
        project = yaml.load(stream, Loader=yaml.FullLoader)
    return project


def load_project_and_defaults():
    defaults_file = f"{os.environ['DEVDOCK_PATH']}/docker/defaults.yaml"
    with open(defaults_file, 'r') as stream:
        defaults = yaml.load(stream, Loader=yaml.FullLoader)
        project = load_project()
    return project, defaults


def get_services(project):
    services = list((project['services'] if 'services' in project else {}).values())
    for p in (project['projects'] if 'projects' in project else {}).values():
        services += list((p['services' if 'services' in p else {}]).values())
    return services


def project_uses_tech(project, filter_tech=None):
    if not filter_tech:
        return False
    services = get_services(project)
    for service in services:
        with open(f"devdock/docker/templates/{service['template'].replace('.','/')}/config.yaml") as stream:
            template_data = stream.read().replace('%=', 'AA')
            template = yaml.load(template_data, Loader=yaml.FullLoader)
        for container_template in template['containers'].values():
            container_stack = container_template['stack'] if 'stack' in container_template else []
            if filter_tech in container_stack:
                return True
    return False
