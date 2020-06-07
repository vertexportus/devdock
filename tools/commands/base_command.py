import gzip
import io
import subprocess
import tarfile
import time
import docker
from abc import ABC, abstractmethod
from utils import env


class BaseCommand(ABC):
    @classmethod
    def create_instance(cls, project_config_manager, args):
        return cls(project_config_manager, args)

    @property
    def project(self):
        return self.__project_config_manager

    @property
    def args(self):
        return self.__args

    def __init__(self, project_config_manager, args):
        self.__project_config_manager = project_config_manager
        self.__args = args

    @abstractmethod
    def process_command(self):
        pass

    # shell helper methods
    @staticmethod
    def run_shell(command, echo=False):
        if echo:
            print(f"+ {command}")
        subprocess.run(command, shell=True)

    @staticmethod
    def run_shell_get_output(command, echo=False):
        if echo:
            print(f"+ {command}")
        result = subprocess.run(command, capture_output=True, shell=True)
        return result.stdout.decode('UTF-8')

    # docker methods
    def container_exec_run(self, container_short_name, command):
        container = self.get_container_by_short_name(container_short_name)
        if container is None:
            raise Exception(f"container '{container_short_name}' not found")
        result = container.exec_run(command, stream=True, demux=False)
        for output in result.output:
            print(output.decode('utf-8'), end='')

    def container_exec_run_get_output(self, container_short_name, command):
        container = self.get_container_by_short_name(container_short_name)
        if container is None:
            raise Exception(f"container '{container_short_name}' not found")
        result = container.exec_run(command, stream=True, demux=False)
        output_result = ""
        for output in result.output:
            output_str = output.decode('utf-8')
            output_result += output_str
            print(output_str, end='')
        return output_result

    @staticmethod
    def get_container_by_short_name(short_name):
        base_name = f"{env.compose_project_name()}_{short_name}"
        client = docker.from_env()
        containers = client.containers.list()
        for container in containers:
            if short_name in container.name:
                return container
        return None

    def get_container_full_name(self, short_name):
        container = self.get_container_by_short_name(short_name)
        if container is None:
            return None
        else:
            return container.name

    def get_project_by_name_or_default_by_tech(self, name: str, tech: str):
        if name:
            project = self.project.get_project_by_name(self.args.project)
            if not project:
                raise Exception(f"project '{self.args.project}' does not exist")
            if tech not in project.tech_stack:
                raise Exception(f"project '{self.args.project}' does not support tech '{tech}'")
        else:
            projects = self.project.get_projects_by_tech(tech)
            if len(projects) < 1:
                raise Exception(f"no project found using tech '{tech}'")
            if len(projects) > 1:
                if not self.args.project:
                    raise Exception(f"need to specify project to run command on with -p|--project")
            project = projects[0]
        return project

    # archive methods
    @staticmethod
    def gunzip_file(file_path):
        with gzip.open(file_path, 'rb') as f:
            file_content = f.read()
        return file_content

    @staticmethod
    def archive_data(data, filename):
        tarstream = io.BytesIO()
        tar = tarfile.TarFile(fileobj=tarstream, mode='w')
        tarinfo = tarfile.TarInfo(name=filename)
        tarinfo.size = len(data)
        tarinfo.mtime = time.time()
        tar.addfile(tarinfo, io.BytesIO(data))
        tar.close()
        tarstream.seek(0)
        return tarstream
