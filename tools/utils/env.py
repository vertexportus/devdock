import os


def cli_command():
    return os.environ['CLI_COMMAND']


def env():
    return os.environ['ENV']


def compose_project_name():
    return os.environ['COMPOSE_PROJECT_NAME'] if 'COMPOSE_PROJECT_NAME' in os.environ else 'devdock'


def project_path(suffix=None):
    return os.path.abspath(f"{os.environ['PROJECT_PATH']}{'/' + suffix if suffix else ''}")


def project_config_path():
    return project_path("project.yaml")


def docker_gen_path(suffix=None):
    return project_path(f"devdock/docker/gen{'/' + suffix if suffix else ''}")


def docker_compose_config_path(for_env=None):
    return docker_gen_path(f"docker-compose-{for_env if for_env else env()}.yaml")
