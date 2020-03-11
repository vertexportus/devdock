import sys

from internals.project_data import load_project_and_defaults, filter_services
from internals.service_version import get_tech_version_from_service

if len(sys.argv) > 1:
    tech = sys.argv[1]
    (project, defaults) = load_project_and_defaults()
    print(':'.join(
        list(map(lambda x: get_tech_version_from_service(tech, x, defaults), filter_services(project, tech)))
        ))
