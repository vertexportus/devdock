import os
import argparse
from commands import base_command
from utils import env, ProjectConfigManager


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
        # docker down
        parser_down = subparser.add_parser('down', help="stops containers")
        parser_down.add_argument('params', nargs=argparse.REMAINDER,
                                 help='additional arguments passed directly into docker-compose down')
        # docker destroy
        parser_destroy = subparser.add_parser('destroy', help="destroys all containers and images")
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
        getattr(self, f"_{self._args.sub_command}_handler")()

    def _up_handler(self):
        if not os.path.isfile(env.docker_compose_config_path()):
            ProjectConfigManager().update()
        self.run_shell("docker-compose down")
        if self._args.rebuild:
            self.run_shell("docker-compose build --no-cache")
        up_args = f"--remove-orphans {'' if self._args.attach else '-d'} {'--build' if self._args.build else ''}"
        self.run_shell(f"docker-compose up {up_args}")

    def _down_handler(self):
        if not os.path.isfile(env.docker_compose_config_path()):
            raise Exception("no docker-compose file generated yet for current ENV")
        down_args = ' '.join(self._args.params) if len(self._args.params) > 0 else '--remove-orphans'
        self.run_shell(f"docker-compose down {down_args}")

    def _destroy_handler(self):
        if not os.path.isfile(env.docker_compose_config_path()):
            raise Exception("no docker-compose file generated yet for current ENV")
        self.run_shell("docker-compose down --rmi all --remove-orphans")

    def _ps_handler(self):
        if not os.path.isfile(env.docker_compose_config_path()):
            raise Exception("no docker-compose file generated yet for current ENV")
        self.run_shell('docker-compose ps')

    def _exec_handler(self):
        if not os.path.isfile(env.docker_compose_config_path()):
            raise Exception("no docker-compose file generated yet for current ENV")
        exec_args = f"{self._args.exec_command} {' '.join(self._args.params) if len(self._args.params) else ''}"
        self.run_shell(f"docker-compose exec {self._args.container} {exec_args}")

    def _logs_handler(self):
        if not os.path.isfile(env.docker_compose_config_path()):
            raise Exception("no docker-compose file generated yet for current ENV")
        logs_args = f"{self._args.container if self._args.container != 'all' else ''} {'-f' if self._args.follow else ''}"
        self.run_shell(f"docker-compose logs {logs_args}")
