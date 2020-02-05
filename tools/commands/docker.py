import os
import argparse
from commands import base_command
from utils import env
import utils.colors


class Docker(base_command.BaseCommand):
    @staticmethod
    def argparse(parser, subparsers):
        parser_main = subparsers.add_parser('docker', help="runs pre-defined docker or docker-compose commands")
        subparser = parser_main.add_subparsers(required=True, dest="sub_command", help="Docker sub commands")
        # docker up
        parser_up = subparser.add_parser('up', help="starts containers")
        parser_up.add_argument('-a', '--attach', action="store_true", help="attach to docker-compose process")
        parser_up.add_argument('--build', action="store_true", help="builds containers if Dockerfiles have changed")
        parser_up.add_argument('--rebuild', action="store_true", help="forces a rebuild of all container images")
        parser_up.add_argument('-g', '--generate', action="store_true", help="generate docker config")
        # docker down
        parser_down = subparser.add_parser('down', help="stops containers")
        parser_down.add_argument('params', nargs=argparse.REMAINDER,
                                 help='additional arguments passed directly into docker-compose down')
        # docker destroy
        parser_destroy = subparser.add_parser('destroy', help="destroys all containers and images")
        # docker build
        parser_build = subparser.add_parser('build', help="builds docker images")
        parser_build.add_argument('--rebuild', action="store_true", help="forces rebuild of image without cache")
        parser_build.add_argument('-g', '--generate', action="store_true", help="generate docker config")
        parser_build.add_argument('containers', nargs=argparse.REMAINDER, help="list of containers to build")
        # docker ps
        parser_ps = subparser.add_parser('ps', help="lists all project running containers and their status")
        # docker exec
        parser_exec = subparser.add_parser('exec', help="runs a command inside a specified container")
        parser_exec.add_argument('container', help="container simplified name (ie: repairq_web_1 is named web)")
        parser_exec.add_argument('exec_command', help="command to run inside specified container")
        parser_exec.add_argument('params', nargs=argparse.REMAINDER,
                                 help="additional parameters for container exec_command")
        # docker logs
        parser_logs = subparser.add_parser('logs', help="shows all container logs (or specified container logs)")
        parser_logs.add_argument('container', help="specific container to show logs from", nargs="?", default="all")
        parser_logs.add_argument('-f', '--follow', action="store_true", help="follow log output")

    def process_command(self):
        getattr(self, f"_{self.args.sub_command}_handler")()

    def _up_handler(self):
        if self.args.generate:
            print(utils.colors.blue("generating docker config..."))
            self.project_config.generate_docker(False)
        else:
            self._check_docker_config(gen=True)
        if self.args.rebuild:
            self.run_shell("docker-compose down")
            self.run_shell("docker-compose build --no-cache")
        up_args = f"--remove-orphans {'' if self.args.attach else '-d'} {'--build' if self.args.build else ''}"
        self.run_shell(f"docker-compose up {up_args}")

    def _down_handler(self):
        self._check_docker_config()
        down_args = ' '.join(self.args.params) if len(self.args.params) > 0 else '--remove-orphans'
        self.run_shell(f"docker-compose down {down_args}")

    def _destroy_handler(self):
        self._check_docker_config()
        self.run_shell("docker-compose down --rmi all --remove-orphans")

    def _build_handler(self):
        if self.args.generate:
            print(utils.colors.blue("generating docker config..."))
            self.project_config.generate_docker(False)
        else:
            self._check_docker_config(gen=True)
        containers = ' '.join(self.args.containers) if len(self.args.containers) > 0 else ''
        args = f"--force-rm {'--no-cache' if self.args.rebuild else ''}"
        self.run_shell(f"docker-compose build {args} {containers}")

    def _ps_handler(self):
        self._check_docker_config()
        self.run_shell('docker-compose ps')

    def _exec_handler(self):
        self._check_docker_config()
        container = self.__get_container_name(self.args.container)
        exec_args = f"{self.args.exec_command} {' '.join(self.args.params) if len(self.args.params) else ''}"
        self.run_shell(f"docker-compose exec {container} {exec_args}")

    def _logs_handler(self):
        self._check_docker_config()
        container = self.__get_container_name(self.args.container) if self.args.container != 'all' else ''
        self.run_shell(f"docker-compose logs {'-f' if self.args.follow else ''} {container}")

    def _check_docker_config(self, gen=False):
        if not os.path.isfile(env.docker_compose_file_path()):
            if gen:
                self.project_config.generate_docker(False)
            else:
                raise Exception(f"no docker-compose file generated yet for current ENV ({env.env()})")

    def __get_container_name(self, path):
        container = self.project_config.get_container_name_by_simple_path(path)
        if not container:
            raise Exception(f"container related to path '{path}' not found")
        return container
