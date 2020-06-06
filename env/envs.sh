#!/usr/bin/env bash
# shellcheck disable=SC2086
# shellcheck disable=SC2155

# colors
color_text="\e[0;36m"
color_text_hl="\e[1;36m"
nc="\e[0;33m"

# versions
echo -e "\n${color_text}devdock version: ${color_text_hl}$([[ -d $DEVDOCK_PATH ]] && cat $DEVDOCK_PATH/VERSION || echo devdock not cloned yet)\e[0;33m"
cmp --silent $PROJECT_PATH/.envrc $DEVDOCK_PATH/env/direnv && echo "" || echo -e "\e[1;33mwarning: \e[0;33mdirenv master file is outdated. please run \e[1;33mdev config env -g\e[0;33m to update\n"

# project/docker
if [[ -z $ENV ]]; then export ENV=dev; fi
if [[ -z $PROJECT_NAME ]]; then export PROJECT_NAME=${PROJECT_PATH##*/}; fi
export COMPOSE_PROJECT_NAME=$PROJECT_NAME;
export COMPOSE_FILE="$DEVDOCK_PATH/docker/gen/docker-compose-$ENV.yaml"

# user/group
export USERID=$(id -u)
export GROUPID=$(id -g)

devdock_utils=$DEVDOCK_PATH/env/utils
# url
url=$(python3 $devdock_utils/get_env_url.py)
if [[ -n $url ]]; then export BASE_URL=$url; else export BASE_URL=localhost; fi

# php
php=$(python3 $devdock_utils/get_tech_version.py php)
if [[ -n $php ]]; then
  if [[ -z $XDEBUG_ENABLE ]]; then export XDEBUG_ENABLE=0; fi
  export XDEBUG_REMOTE_HOST=$(ip -4 addr show docker0 | grep -Po 'inet \K[\d.]+')
fi

# node
node=$(python3 $devdock_utils/get_tech_version.py node)
angular=$(python3 $devdock_utils/get_tech_version.py angular)

# dotnetcore
dotnetcore=$(python3 $devdock_utils/get_tech_version.py dotnetcore)

# dbs
postgres=$(python3 $devdock_utils/get_tech_version.py postgres)

# cloud local services
minio=$(python3 $devdock_utils/get_tech_version.py minio)

## show information of current env
echo -e "${color_text} Project   :   ${color_text_hl}$PROJECT_NAME"
echo -e "${color_text} Env       :   ${color_text_hl}$ENV"
echo -e "${color_text} Base URL  :   ${color_text_hl}$BASE_URL"
if [[ -n $php ]]; then echo -e "${color_text} PHP       :   ${color_text_hl}$php $([ $XDEBUG_ENABLE -eq 0 ] && echo no-xdebug || echo xdebug)"; fi
if [[ -n $node ]]; then
  node_adds=
  if [[ -n $angular ]]; then node_adds="(angular: $angular)"; fi
  echo -e "${color_text} Node      :   ${color_text_hl}$node $node_adds"
fi
if [[ -n $dotnetcore ]]; then echo -e "${color_text} .net Core :   ${color_text_hl}$dotnetcore"; fi
if [[ -n $postgres ]]; then echo -e "${color_text} Postgres  :   ${color_text_hl}$postgres"; fi
if [[ -n $minio ]]; then echo -e "${color_text} Minio(S3) :   ${color_text_hl}$minio"; fi
echo -e "${nc}"
