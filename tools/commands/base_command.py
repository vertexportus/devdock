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
    def project_config(self):
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

    # docker methods
    def container_exec_run(self, container_short_name, command):
        container = self.get_container_by_short_name(container_short_name)
        if container is None:
            raise Exception(f"container '{container_short_name}' not found")
        result = container.exec_run(command, stream=True, demux=False)
        for output in result.output:
            print(output.decode('utf-8'), end='')

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
            project = self.project_config.get_project_by_name(self.args.project)
            if not project:
                raise Exception(f"project '{self.args.project}' does not exist")
            if 'php' not in project.tech_stack:
                raise Exception(f"project '{self.args.project}' does not support tech 'php'")
        else:
            projects = self.project_config.get_projects_by_tech(tech)
            if len(projects) > 1:
                if not self.args.project:
                    raise Exception(f"need to specify php project to run composer on with -p|--project")
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
