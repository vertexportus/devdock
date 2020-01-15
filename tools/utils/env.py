import os
import re


def cli_command():
    return os.environ['CLI_COMMAND']


def env():
    return os.environ['ENV']


def compose_project_name():
    return os.environ['COMPOSE_PROJECT_NAME'] if 'COMPOSE_PROJECT_NAME' in os.environ else 'devdock'


def project_path(suffix):
    return os.path.abspath(f"{os.environ['PROJECT_PATH']}{'/'+suffix if suffix else ''}")


def project_config_path():
    return project_path("project.yaml")

# def with_default(var_name, default):
#     return os.environ[var_name] if var_name in os.environ else default
#
#
# def try_get(var_name):
#     if var_name in os.environ:
#         return os.environ[var_name]
#     else:
#         raise Exception(f"'{var_name}' not set in env")
#
#

#
#
# def git_use_https():
#     return with_default('GIT_USE_HTTPS', '0') == '1'
#
#
# def compose_project_name():
#     return with_default('COMPOSE_PROJECT_NAME', 'compose')
#
#
# def services(override=None):
#     services_map = {}
#     raw_services = override.split(',') if override else with_default('SERVICES', '').split(',')
#     for raw_service in raw_services:
#         if ':' in raw_service:
#             raw_service_split = raw_service.split(':')
#             services_map[raw_service_split[0]] = raw_service_split[1]
#         else:
#             services_map[raw_service] = raw_service
#     return services_map
#
#
# def is_env_projects_set():
#     return 'PROJECTS' in os.environ
#
#
# def projects():
#     projects_map = {}
#     project_names = map(lambda p: p.strip(), os.environ['PROJECTS'].split(','))
#     for raw_project_name in list(project_names):
#         project_var_name = re.sub('(?!^)([A-Z]+)', r'_\1', raw_project_name).upper()
#         var_folder = f"PROJECT_{project_var_name}_FOLDER"
#         var_git = f"PROJECT_{project_var_name}_GIT"
#         var_services = f"PROJECT_{project_var_name}_SERVICES"
#         project_name = raw_project_name.upper()
#         projects_map[raw_project_name] = {
#             "repo_url": try_get(var_git),
#             "folder": os.environ[var_folder] if var_folder in os.environ else f"src/{project_var_name.lower()}",
#             "services": services(os.environ[var_services]) if var_services in os.environ else {}
#         }
#     return projects_map
