import os
import json

from utils import env
from utils.templates import Templates


def generate_build_files(src_paths: list, dest_path: str, templates: Templates, **template_params):
    changed = False
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
                rendered_file_data = templates.render_template(template_src_file, **template_params)
                if os.path.exists(dest_file):
                    with open(dest_file, 'r') as stream:
                        orig_data = stream.read()
                    if orig_data == rendered_file_data:
                        continue
                with open(dest_file, 'w') as stream:
                    stream.write(rendered_file_data)
                changed = True
    return changed


rebuild_marker = []


def rebuild_marker_reset():
    global rebuild_marker
    rebuild_marker = []
    rebuild_file_path = env.docker_gen_rebuild_flag_path()
    if os.path.exists(rebuild_file_path):
        os.remove(rebuild_file_path)
    return rebuild_marker


def rebuild_marker_load():
    global rebuild_marker
    rebuild_marker = []
    rebuild_file_path = env.docker_gen_rebuild_flag_path()
    if os.path.exists(rebuild_file_path):
        with open(rebuild_file_path, 'r') as stream:
            rebuild_marker = json.load(stream)
    return rebuild_marker


def rebuild_marker_append(value: str):
    global rebuild_marker
    if value not in rebuild_marker:
        rebuild_marker.append(value)
    return rebuild_marker


def rebuild_marker_save():
    global rebuild_marker
    if len(rebuild_marker) > 0:
        rebuild_file_path = env.docker_gen_rebuild_flag_path()
        with open(rebuild_file_path, 'w') as stream:
            json.dump(rebuild_marker, stream)
    return rebuild_marker
