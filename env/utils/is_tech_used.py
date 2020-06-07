import sys

from internals.project_data import load_project, project_uses_tech

if len(sys.argv) > 1:
    tech = sys.argv[1]
    project = load_project()
    print(1 if project_uses_tech(project, tech) else 0)
