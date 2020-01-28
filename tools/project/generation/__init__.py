import importlib.util
import inspect as inspector
import os
import shutil

from utils import env


def generate_build_files(src_paths: list, dest_path: str, mapping: dict):
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
                dest_file = os.path.join(dest_dir, filename)
                if filename.endswith('.py'):
                    data = run_generator(src_file, mapping)
                    with open(dest_file.replace('.py', ''), 'w') as stream:
                        stream.write(data)
                else:
                    if os.path.exists(dest_file):
                        if os.path.samefile(src_file, dest_file):
                            continue
                        os.remove(dest_file)
                    shutil.copy(src_file, dest_file)


def run_generator(script_path: str, mapping: dict) -> str:
    module_name = os.path.basename(script_path.replace('.py', ''))
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    inspect = inspector.getmembers(module, inspector.isfunction)
    if len(inspect) < 1:
        raise Exception(f"error running generator '{script_path.replace(env.docker_template_path(), '')}'")
    _, fn_generator = next(iter(filter(lambda x: x[0] == 'generate', inspect)), None)
    if not fn_generator:
        raise Exception(f"generator script '{script_path.replace(env.docker_template_path(), '')}' "
                        "does not contain a 'generate()' function")
    return fn_generator(mapping)
