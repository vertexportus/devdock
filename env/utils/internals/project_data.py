import yaml
import os


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


def filter_services(project, filter_tech=None):
    return list(filter(lambda x: filter_tech in x['template'], get_services(project)))
