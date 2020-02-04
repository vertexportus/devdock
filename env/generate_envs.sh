#!/usr/bin/env bash

# versions
echo -e "\n\e[0;36mdevdock version: \e[1;36m$([[ -d $DEVDOCK_PATH ]] && cat $DEVDOCK_PATH/VERSION || echo devdock not cloned yet)\e[0;33m"
cmp --silent $PROJECT_PATH/.envrc $DEVDOCK_PATH/env/direnv && echo "" || echo -e "\e[1;33mwarning: \e[0;33mdirenv master file is outdated. please run \e[1;33mdev config env -g\e[0;33m to update\n"

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
is_php_used=$(cat "${PROJECT_PATH}/project.yaml" | grep -Po "template: php")
if [[ -n $is_php_used ]]; then
  if [[ -z $XDEBUG_ENABLE ]]; then export XDEBUG_ENABLE=0; fi
  export XDEBUG_REMOTE_HOST=$(ip -4 addr show docker0 | grep -Po 'inet \K[\d.]+')
fi

$DEVDOCK_PATH/env/print_envs.sh
