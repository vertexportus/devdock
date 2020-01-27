class ContainerTemplateEnv:
    prefix: str
    prefixed: dict
    exported: dict
    imported: dict
    environment: dict

    def __init__(self, container, data):
        self.container = container
        self.prefix = container.template.service.env_prefix.upper()
        self.prefixed = {k: f"{self.prefix}_{v.upper()}"
                         for k, v in (data['prefixed'] if 'prefixed' in data else {}).items()}
        exported_raw = (data['exported'] if 'exported' in data else []) + ['host']
        self.exported = dict(zip(exported_raw, list(map(lambda e: f"{self.prefix}_{e.upper()}", exported_raw))))
        self.imported = data['imported'] if 'imported' in data else {}
        self.environment = {}

    def calculate_final_env(self):
        # calculate imported
        prefixed = {k: f"${{{v}}}" for k, v in self.prefixed.items()}
        imported = {k: self.import_env(v) for k, v in self.imported.items()}
        self.environment = {**prefixed, **imported}

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
        if len(self.environment):
            compose_service['environment'] = {**self.environment}

    @classmethod
    def __dict_to_str(cls, d):
        return str.join('\n', list(map(cls.__env_map, {k: f"{k}={v}" for k, v in d.items()}.values())))

    @staticmethod
    def __env_map(e):
        return f"             {e}"
