# devdock
Set of tools to help manage a docker-oriented development environment

## temp example project.yaml

```
projects:
  laravel:
    github: username/laravel.git
    services:
      laravel:
        template: php.laravel.nginx
        database: db
        ports:
          - http_port
        env_files: true

services:
  db:
    template: postgres
```
## temp .envrc

```
if [ -f ".env" ]; then dotenv; else echo "no .env file"; fi
PATH_add "$PWD/devdock/bin"

export PROJECT_PATH=$PWD
if [ -n "$PROJECT_NAME" ]; then export COMPOSE_PROJECT_NAME=$PROJECT_NAME; else export COMPOSE_PROJECT_NAME=${PWD##*/}; fi
if [ -z $ENV ]; then export ENV=dev; fi
export COMPOSE_FILE="$PWD/devdock/docker/gen/docker-compose-$ENV.yaml"

export USERID=$(id -u)
export GROUPID=$(id -g)
```