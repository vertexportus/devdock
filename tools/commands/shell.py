from commands import base_command


class Shell(base_command.BaseCommand):
    @staticmethod
    def argparse(parser, subparsers):
        parser_main = subparsers.add_parser('shell', help="runs a shell inside a specified container")
        parser_main.add_argument('container', help="container to run shell in")

    def process_command(self):
        container = self.project.get_container_name_by_simple_path(self.args.container)
        if not container:
            raise Exception(f"container related to path '{self.args.container}' not found")
        self.run_shell(
            f"docker-compose exec {container} sh -c \"which bash > /dev/null 2>&1 && bash || sh\"")
