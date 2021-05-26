#!/usr/bin/env bash
# shellcheck disable=SC2086
# shellcheck disable=SC2155

python=python3.9

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
is_tech_used="$python ${devdock_utils}/is_tech_used.py"
get_tech_version="$python $devdock_utils/get_tech_version.py"
# url
url=$($python $devdock_utils/get_env_url.py)
if [[ -n $url ]]; then export BASE_URL=$url; else export BASE_URL=localhost; fi

# php
php=$($is_tech_used minio)
if [[ $php  ]]; then
  if [[ -z $XDEBUG_ENABLE ]]; then
    export XDEBUG_ENABLE=0
  else
    export XDEBUG_REMOTE_HOST=host.docker.internal
  fi
fi

# cloud local services
localaws=$($is_tech_used localaws)
s3=$($is_tech_used minio)

## show information of current env
echo -e "${color_text} Project   :   ${color_text_hl}$PROJECT_NAME"
echo -e "${color_text} Env       :   ${color_text_hl}$ENV"
echo -e "${color_text} Base URL  :   ${color_text_hl}$BASE_URL"
echo -e "${color_text} Versions  :   ${color_text_hl}$($get_tech_version)"
if [ $localaws -eq 1 ]; then
  printf "${color_text} Local AWS :   $color_text_hl"
  if [ $s3 -eq 1 ]; then echo "S3 "; fi
else
  echo -e "${color_text} Local AWS :   ${color_text_hl}None"
fi
echo -e "${nc}"
