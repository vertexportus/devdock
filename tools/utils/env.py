import os


def cli_command() -> str:
    return os.environ['CLI_COMMAND']


def env() -> str:
    return os.environ['ENV']


def compose_project_name() -> str:
    return os.environ['COMPOSE_PROJECT_NAME'] if 'COMPOSE_PROJECT_NAME' in os.environ else 'devdock'


def project_path(suffix=None) -> str:
    return os.path.abspath(f"{os.environ['PROJECT_PATH']}{'/' + suffix if suffix else ''}")


def reverse_project_path(path) -> str:
    return path.replace(project_path(), "${PROJECT_PATH}")


def project_config_file_path() -> str:
    return project_path("project.yaml")


def docker_template_path(suffix=None) -> str:
    return project_path(f"devdock/docker/templates{'/' + suffix if suffix else ''}")


def docker_gen_path(suffix=None) -> str:
    return project_path(f"devdock/docker/gen{'/' + suffix if suffix else ''}")


def docker_compose_file_path(for_env=None) -> str:
    return docker_gen_path(f"docker-compose-{for_env if for_env else env()}.yaml")


def git_use_ssh():
    return bool(os.environ['GIT_USE_SSH']) if 'GIT_USE_SSH' in os.environ else True
