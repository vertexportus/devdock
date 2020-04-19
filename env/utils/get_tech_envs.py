import sys

from internals.project_data import load_project, filter_services


if len(sys.argv) > 1:
    tech = sys.argv[1]
    project = load_project()
    services = []
    print(services)
