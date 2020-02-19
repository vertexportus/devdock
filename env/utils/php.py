import yaml
import os


def get_php_version_from_service(service):
    global defaults
    if 'version' in service:
        version_attr = service['version']
        if type(version_attr) == str:
            version = version_attr
        elif 'php' in version_attr:
            version = version_attr['php']
        else:
            version = '-'
    else:
        version = defaults['php']['version']
    return str(version)


defaults_file = f"{os.environ['DEVDOCK_PATH']}/docker/defaults.yaml"
project_file = f"{os.environ['PROJECT_PATH']}/project.yaml"
with open(project_file, 'r') as stream:
    project = yaml.load(stream, Loader=yaml.FullLoader)
with open(defaults_file, 'r') as stream:
    defaults = yaml.load(stream, Loader=yaml.FullLoader)

services = list((project['services'] if 'services' in project else {}).values())
for p in (project['projects'] if 'projects' in project else {}).values():
    services += list((p['services' if 'services' in p else {}]).values())
php_services = list(filter(lambda x: 'php' in x['template'], services))
result = ':'.join(list(map(lambda x: get_php_version_from_service(x), php_services)))
print(result)
