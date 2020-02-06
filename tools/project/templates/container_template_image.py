import re

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
            image = {**self.image}
            if type(image['context']) is list:
                contexts = image['context']
                image['context'] = contexts[0]
            else:
                contexts = [image['context']]
            compose_service['build'] = image
            template_params = {
                'env': env.get_env_dict(),
                'container': self.container,
                'siblings': self.container.template.containers,
                'service': self.container.template.service,
                'project': self.container.template.service.project,
                'defaults': self.container.template.service.master.defaults
            }
            generate_build_files(contexts, contexts[0], self.container.template.service.master.templates, **template_params)

            #                      {
            #     'container': self.container,
            #     'siblings': self.container.template.containers
            # })
        else:
            compose_service['image'] = self.image

    @classmethod
    def __dict_to_str(cls, d):
        return str.join('\n         - ', list(map(lambda e: f"{e}", {k: f"{k}={v}" for k, v in d.items()}.values())))

    def __as_image(self, image):
        self.is_build = False
        self.image = f"{image['name']}:{image['tag']}"
        pass

    def __as_build(self, build):
        self.is_build = True
        self.image = build
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
