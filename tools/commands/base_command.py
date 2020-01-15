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
    def create_instance(cls, args):
        return cls(args)

    def __init__(self, args):
        self._args = args

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
