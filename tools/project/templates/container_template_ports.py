class ContainerTemplatePorts:
    mapping: dict

    def __init__(self, template, data):
        self.template = template
        self.mapping = {}
        for port_number in data:
            port_config = data[port_number]
            if port_config and 'env' in port_config:
                self.mapping[port_number] = template.env.exported[port_config['env']]
            else:
                self.mapping[port_number] = port_number
        pass

    def __str__(self):
        ports = str.join('\n         - ',
                         list(map(lambda e: f"  {e}", {k: f"{k}={v}" for k, v in self.mapping.items()}.values())))
        return f"ports:\n        {ports}"

    def generate_compose(self, compose_service):
        if len(self.mapping) > 1:
            compose_service['ports'] = list({k: f"${{{v}:-{k}}}:{k}" for k, v in self.mapping.items()}.values())
