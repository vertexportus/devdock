#!/usr/bin/env bash

# project/docker
if [[ -z $ENV ]]; then export ENV=dev; fi
if [[ -z $PROJECT_NAME ]]; then export PROJECT_NAME=${PROJECT_PATH##*/}; fi
export COMPOSE_PROJECT_NAME=$PROJECT_NAME;
export COMPOSE_FILE="$DEVDOCK_PATH/docker/gen/docker-compose-$ENV.yaml"

# user/group
export USERID=$(id -u)
export GROUPID=$(id -g)

# url
url=$(python3 $DEVDOCK_PATH/env/get_env_url.py)
if [[ -n $url ]]; then export BASE_URL=$url; else export BASE_URL=localhost; fi

# php xdebug
if [[ -z $XDEBUG_ENABLE ]]; then export XDEBUG_ENABLE=0; fi
is_php_used=$(cat "${PROJECT_PATH}/project.yaml" | grep -Po "template: php")
if [[ -n $is_php_used ]]; then export XDEBUG_REMOTE_HOST=$(ip -4 addr show docker0 | grep -Po 'inet \K[\d.]+'); fi
