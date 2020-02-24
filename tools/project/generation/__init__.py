import os

from utils import env
from utils.templates import Templates


def generate_build_files(src_paths: list, dest_path: str, templates: Templates, **template_params):
    for src_path in src_paths:
        build_src_path = env.docker_template_path(src_path)
        build_dest_path = env.docker_gen_path(dest_path)
        if not os.path.exists(build_src_path):
            continue
        for src_dir, dirs, files in os.walk(build_src_path):
            dest_dir = src_dir.replace(build_src_path, build_dest_path, 1)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            for filename in files:
                src_file = os.path.join(src_dir, filename)
                template_src_file = src_file.replace(env.docker_template_path(), '')
                dest_file = os.path.join(dest_dir, filename)
                if os.path.exists(dest_file):
                    if os.path.samefile(src_file, dest_file):
                        continue
                    os.remove(dest_file)
                rendered_file_data = templates.render_template(template_src_file, **template_params)
                with open(dest_file, 'w') as stream:
                    stream.write(rendered_file_data)
