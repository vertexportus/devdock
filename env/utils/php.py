from internals.project_data import load_project_and_defaults, filter_services
from internals.service_version import get_tech_version_from_service

(project, defaults) = load_project_and_defaults()
print(':'.join(
    list(map(lambda x: get_tech_version_from_service('php', x, defaults), filter_services(project, 'php')))))
