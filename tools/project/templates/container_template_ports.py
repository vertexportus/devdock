from pprint import pp


class ContainerTemplatePorts:
    mapping: dict

    def __init__(self, container, data):
        self.container = container
        self.mapping = {}
        for port_name, port_config in data.items():
            if type(port_config) is dict:
                self.mapping[port_name] = {
                    'external': f"${{{container.env.exported[port_config['env']]}:-{port_config['default']}}}",
                    'internal': port_config['default']
                }
            else:
                self.mapping[port_name] = {'external': port_config, 'internal': port_config}

    def __str__(self):
        ports = str.join('\n         - ',
                         list(map(lambda e: f"  {e}", {k: f"{k}={v}" for k, v in self.mapping.items()}.values())))
        return f"ports:\n        {ports}"

    def generate_compose(self, compose_service):
        service_ports_config = self.container.template.service.ports
        if service_ports_config and len(self.mapping) > 0:
            if type(service_ports_config) is list:
                compose_service['ports'] = list({k: f"{v['external']}:{v['internal']}"
                                                 for k, v in self.mapping.items() if
                                                 k in service_ports_config}.values())
            else:
                compose_service['ports'] = list(
                    map(lambda x: f"{x['external']}:{x['internal']}", self.mapping.values()))
