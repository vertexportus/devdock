import yaml
from jinja2 import Template


# def load_yaml_template(template_file_path, **kwargs):
#     return yaml.load(load_template(template_file_path, **kwargs), Loader=yaml.FullLoader)
#
#
# def load_template(template_file_path, **kwargs):
#     with open(template_file_path, 'r') as stream:
#         text = stream.read()
#     template = Template(text)
#     return template.render(**kwargs)


# def parse_vars(source, mapping) -> str:
#     dest = str(source)
#     regex = re.compile(r"%\((.+)\)")
#     result = regex.findall(source)
#     # if regex found variable dot path
#     for raw_var in result:
#         default_val = None
#         # take care to allow for default values
#         if ':' in raw_var:
#             [dot_path, default_val] = raw_var.split(':')
#         else:
#             dot_path = raw_var
#         # take care to allow for method transforms
#         if '!' in dot_path:
#             [dot_path, func] = dot_path.split('!')
#         else:
#             func = None
#         # get value
#         dot_path_split = dot_path.split('.')
#         obj = mapping
#         for attr_name in dot_path_split:
#             if type(obj) is dict and attr_name in obj:
#                 obj = obj[attr_name]
#             elif hasattr(obj, attr_name):
#                 obj = getattr(obj, attr_name)
#             else:
#                 obj = None
#                 break
#         val = obj
#         # run transform function if requested
#         if func and hasattr(val, func):
#             val = getattr(val, func)()
#
#         if not val:
#             if not default_val:
#                 raise Exception(f"'{dot_path}' not found in mapping")
#             else:
#                 dest = dest.replace(f"%({raw_var})", default_val)
#         else:
#             dest = dest.replace(f"%({raw_var})", str(val))
#     return dest