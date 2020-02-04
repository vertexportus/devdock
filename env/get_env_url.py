import os
import re


project_name = os.environ['PROJECT_NAME']
regex = re.compile(r"\d+\.\d+\.\d+\.\d+\s+([\w.]+)\s+#\s" + project_name + r"\scommand\sregistry")
with open("/etc/hosts", "r") as stream:
    hosts_config = stream.read()
matches = regex.findall(hosts_config)
if len(matches) > 0:
    print(matches[0])
