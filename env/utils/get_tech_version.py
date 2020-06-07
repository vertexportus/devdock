import sys

from internals.project_data import load_project, filter_services
from internals.service_version import get_tech_version_from_service

if len(sys.argv) > 1:
    tech = sys.argv[1]
    project = load_project()
    with open('.versions', 'r') as stream:
        project = yaml.load(stream, Loader=yaml.FullLoader)
    print(':'.join(
        list(map(lambda x: get_tech_version_from_service(tech, x, defaults), filter_services(project, tech)))
        ))
