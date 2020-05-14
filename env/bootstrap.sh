#!/usr/bin/env bash

function check_tool() {
  if ! [ -x "$(command -v $1)" ]; then
    echo "$1 is not installed. quiting..."
    exit
  fi
}

function bootstrap_devdock() {
  git clone $1 devdock
  cp devdock/env/direnv .envrc
  direnv allow
  mkdir bin
  cp devdock/env/dev bin/dev
  chmod +x bin/dev
}

read -r -d '' project_prg << EOM
import os
import re
import yaml
with open('project.yaml', 'r') as stream:
  p = yaml.load(stream, Loader=yaml.FullLoader)
if 'devdock' in p:
  d=p['devdock']
  if os.path.isfile('.env'):
    with open('.env', 'r') as stream:
      env = stream.read()
    m = re.search(r"GIT_USE_SSH=(?P<ssh>\w+)", env)
    if m is not None:
      ssh=m.group('ssh') != '0'
    else:
      ssh=True
  else:
    ssh=True
  if 'github' in d:
    print(f"{'git@github.com:' if ssh else 'https://github.com/'}{d['github']}")
  elif 'repo' in d:
    print(d['repo'])
EOM

check_tool "python3.8"
check_tool "git"
check_tool "direnv"

if [ -f 'project.yaml' ]; then
  repo=$(python3.8 -c "$project_prg")
  bootstrap_devdock $repo
else
  repo=${REPO:-git@github.com:vertexportus/devdock.git}
  bootstrap_devdock $repo
  dev config init --repo ${repo}
fi
