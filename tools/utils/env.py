import os


def cli_command() -> str:
    return os.environ['CLI_COMMAND']


def env() -> str:
    return os.environ['ENV']


def get_env_dict() -> dict:
    return {
        'env': env()
    }


def project_name() -> str:
    return os.environ['PROJECT_NAME']


def compose_project_name() -> str:
    return os.environ['COMPOSE_PROJECT_NAME'] if 'COMPOSE_PROJECT_NAME' in os.environ else 'devdock'


def project_path(suffix=None) -> str:
    return os.path.abspath(f"{os.environ['PROJECT_PATH']}{'/' + suffix if suffix else ''}")


def devdock_path(suffix=None) -> str:
    return project_path(f"devdock{'/' + suffix if suffix else ''}")


def reverse_project_path(path) -> str:
    return path.replace(project_path(), "${PROJECT_PATH}")


def project_config_file_path() -> str:
    return project_path("project.yaml")


def env_template_path(path) -> str:
    return devdock_path(f"env/{path}")


def docker_template_path(suffix=None) -> str:
    return devdock_path(f"docker/templates{'/' + suffix if suffix else ''}")


def docker_gen_path(suffix=None) -> str:
    return devdock_path(f"docker/gen{'/' + suffix if suffix else ''}")


def docker_compose_file_path(for_env=None) -> str:
    return docker_gen_path(f"docker-compose-{for_env if for_env else env()}.yaml")


def git_use_ssh():
    return bool(os.environ['GIT_USE_SSH']) if 'GIT_USE_SSH' in os.environ else True


def env_var_format(var_name, default=None, open_symbol='${', close_symbol='}'):
    return (f"{open_symbol}{var_name}{':-' if default is not None else ''}"
            f"{default if default is not None else ''}{close_symbol}")


def env_var_nested_format(var_name, default_var_name, default=None):
    return env_var_format(
        var_name,
        env_var_format(default_var_name, default)
    )
