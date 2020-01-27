import os
import re
import shutil

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
            overrides = []
            if type(image['context']) is list:
                context = regex.sub(for_env, image['context'][0])
                overrides = list(map(lambda x: regex.sub(for_env, x), image['context'][1:]))
            else:
                context = regex.sub(for_env, image['context'])
            image['context'] = context
            compose_service['build'] = image
            # copy base build context structure
            build_orig_path = env.docker_template_path(context)
            build_dest_path = env.docker_gen_path(context)
            if os.path.isdir(build_dest_path):
                shutil.rmtree(build_dest_path)
            shutil.copytree(build_orig_path, build_dest_path)
            # do overrides if requested
            for override_context in overrides:
                override_orig_path = env.docker_template_path(override_context)
                if not os.path.isdir(override_orig_path):
                    continue
                for src_dir, dirs, files in os.walk(override_orig_path):
                    dest_dir = src_dir.replace(override_orig_path, build_dest_path, 1)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    for file_name in files:
                        src_file = os.path.join(src_dir, file_name)
                        dest_file = os.path.join(dest_dir, file_name)
                        if os.path.exists(dest_file):
                            if os.path.samefile(src_file, dest_file):
                                continue
                            os.remove(dest_file)
                        shutil.copy(src_file, dest_file)
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
