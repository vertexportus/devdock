#!/usr/bin/env bash

function check_tool() {
  if ! [ -x "$(command -v $1)" ]; then
    echo "$1 is not installed. quiting..."
    exit
  fi
}

check_tool "python3.8"
check_tool "git"
check_tool "direnv"

git clone ${REPO:-git@github.com:vertexportus/devdock.git} devdock
cp devdock/direnv .envrc
direnv allow
mkdir bin
cp devdock/env/dev bin/dev
chmod +x bin/dev