from commands import base_command
from project import ProjectConfigManager


class Shell(base_command.BaseCommand):
    @staticmethod
    def argparse(parser, subparsers):
        parser_main = subparsers.add_parser('shell', help="runs a shell inside a specified container")
        parser_main.add_argument('container', help="container to run shell in")

    def process_command(self):
        manager = ProjectConfigManager()
        if '.' in self._args.container:
            container = None
            projects = manager.get_projects()
            [base, path] = self._args.container.split('.', 1)
            if base in projects:
                project = projects[base]
                if base in project.services:
                    service = project.services[base]
                    container = service.containers[path]
                else:
                    if '.' in path:
                        [service_name, container_name] = path.split('.')
                        service = project.services[service_name]
                        container = service.containers[container_name] if service else None
                    else:
                        service = project.services[path]
                        container = service.containers[next(iter(service.containers))]
            else:
                service = manager.get_service_by_path(base)
                container = service.containers[path]
        else:
            service = manager.get_service_by_path(self._args.container)
            container = service.containers[next(iter(service.containers))]

        if not container:
            raise Exception(f"container related to path '{self._args.container}' not found")
        self.run_shell(
            f"docker-compose exec {container.fullname} sh -c \"which bash > /dev/null 2>&1 && bash || sh\"")
