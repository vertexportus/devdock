import sys
import yaml


with open('.versions', 'r') as stream:
    versions = yaml.load(stream, Loader=yaml.FullLoader)
techs = [f"{k}:{v}" for k, v in versions.items()]
print(' '.join(techs))
