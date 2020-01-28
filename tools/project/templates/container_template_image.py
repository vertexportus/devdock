import os
import re
import shutil

from project.generation import generate_build_files
from utils import env


class ContainerTemplateImage:
    is_build: bool
    image: dict or str

    def __init__(self, container, data):
        self.container = container
        if 'image' in data:
            self.__as_image(data['image'])
        elif 'build' in data:
            self.__as_build(data['build'])
        else:
            raise Exception(f"No build or image config set on template '{container.name}'")

    def __str__(self):
        return (f"image(build:{self.is_build}):\n"
                f"         - {self.image if type(self.image) is str else self.__dict_to_str(self.image)}\n")

    def generate_compose(self, compose_service, for_env):
        if self.is_build:
            regex = re.compile(r"\${*ENV}*")
            image = {**self.image}
            image_context = image['context']
            contexts = list(map(lambda x: regex.sub(for_env, x), image_context))\
                if type(image_context) is list else [regex.sub(for_env, image_context)]
            image['context'] = contexts[0]
            compose_service['build'] = image
            generate_build_files(contexts, contexts[0], {
                'container': self.container,
                'siblings': self.container.template.containers
            })
        else:
            compose_service['image'] = self.image

    @classmethod
    def __dict_to_str(cls, d):
        return str.join('\n         - ', list(map(lambda e: f"{e}", {k: f"{k}={v}" for k, v in d.items()}.values())))

    def __as_image(self, image):
        self.is_build = False
        self.image = f"{image['name']}:{self.container.template.service.parse_var(image['tag'])}"
        pass

    def __as_build(self, build):
        self.is_build = True
        self.image = self.__process_vars(build)
        pass

    def __process_vars(self, value):
        if type(value) is str:
            return self.container.template.service.parse_var(value)
        elif type(value) is dict:
            return {k: self.__process_vars(v) for k, v in value.items()}
        elif type(value) is list:
            return list(map(lambda x: self.__process_vars(x), value))
        else:
            raise Exception(f"invalid data type in template '{self.container.template.name}'")
