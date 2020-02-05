import os
from pprint import pp

from utils import env


class ContainerTemplateEnv:
    prefix: str
    mapped: dict
    prefixed: dict
    exported: dict
    imported: dict
    environment: dict
    env_file: list

    def __init__(self, container, data):
        self.container = container
        self.prefix = container.template.service.env_prefix.upper()
        mapped_raw = data['mapped'] if 'mapped' in data else []
        if type(mapped_raw) == list:
            mapped_raw_upper = list(map(lambda x: x.upper(), mapped_raw))
            self.mapped = dict(zip(mapped_raw_upper, mapped_raw_upper))
        else:
            self.mapped = {k: v.upper() for k, v in mapped_raw}
        self.prefixed = {k: f"{self.prefix}_{v.upper()}"
                         for k, v in (data['prefixed'] if 'prefixed' in data else {}).items()}
        exported_raw = (data['exported'] if 'exported' in data else []) + ['host']
        self.exported = dict(zip(exported_raw, list(map(lambda e: f"{self.prefix}_{e.upper()}", exported_raw))))
        self.imported = data['imported'] if 'imported' in data else {}
        env_files = container.template.service.env_files
        self.env_file = self.__env_files(env_files) if env_files else []
        self.environment = {}

    def calculate_final_env(self):
        # calculate imported
        env_files_data = ''
        for env_file in self.env_file:
            with open(env_file) as stream:
                env_files_data += "\n" + stream.read()
        mapped = {k: f"${{{v}}}" for k, v in self.mapped.items() if k not in env_files_data}
        prefixed = {k: f"${{{v}}}" for k, v in self.prefixed.items() if k not in env_files_data}
        imported = {k: self.import_env(v) for k, v in self.imported.items() if k not in env_files_data}
        self.environment = {**mapped, **prefixed, **imported}

    def import_env(self, dot_path):
        [attr, var] = dot_path.split('.')
        service_path = getattr(self.container.template.service, attr)
        service = self.container.template.service.project.master.get_service_by_path(service_path)
        if not service:
            raise Exception(f"service '{service_path}' not found")
        exported_var = None
        for container in service.template.containers.values():
            if var in container.env.exported:
                exported_var = f"${{{container.env.exported[var]}}}"
                break
        if not exported_var:
            raise Exception(f"exported var '{dot_path}' not found")
        return exported_var

    def __str__(self):
        prefixed = f"         - prefixed: \n{self.__dict_to_str(self.prefixed)}\n" if len(self.prefixed) > 0 else ""
        exported = f"         - exported: \n{self.__dict_to_str(self.exported)}\n" if len(self.exported) > 0 else ""
        imported = f"         - imported: \n{self.__dict_to_str(self.imported)}\n" if len(self.imported) > 0 else ""
        environment = f"         - environment: \n{self.__dict_to_str(self.environment)}\n" \
            if len(self.environment) > 0 else ""
        return (f"env:\n"
                f"         - prefix: {self.prefix}\n{prefixed}{exported}{imported}{environment}")

    def generate_compose(self, compose_service):
        if len(self.environment) > 0:
            compose_service['environment'] = {**self.environment}
        if len(self.env_file) > 0:
            compose_service['env_file'] = list(
                map(lambda x: x.replace(env.project_path(), '${PROJECT_PATH}'), self.env_file)
            )

    def __env_files(self, files) -> list:
        result = []
        if type(files) is bool:
            result.append(env.project_path('.env'))
            service_env = env.project_path(f".{self.container.template.service.name}.env")
            if os.path.isfile(service_env):
                result.append(service_env)
        else:
            result = list(filter(lambda x: os.path.isfile(x), map(lambda x: env.project_path(x), files)))
        return result

    @classmethod
    def __dict_to_str(cls, d):
        return str.join('\n', list(map(cls.__env_map, {k: f"{k}={v}" for k, v in d.items()}.values())))

    @staticmethod
    def __env_map(e):
        return f"             {e}"
