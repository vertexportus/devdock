import os
import sys
import yaml

if not os.path.isfile('.versions'):
    print('-')
    exit(0)
with open('.versions', 'r') as stream:
    versions = yaml.load(stream, Loader=yaml.FullLoader)
techs = [f"{k}:{v}" for k, v in versions.items()]
print(' '.join(techs))
