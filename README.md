# devdock
Set of tools to help manage a docker-oriented development environment

## temp example project.yaml

```
projects:
  api:
    repo: git@github.com:vertexportus/moneycloud-api.git
    services:
      api:
        template: elixir.phoenix

services:
  db:
    template: postgres
    ports: true
    env_map:
      user: $DB_USER
      password: $DB_PASSWORD
      database: $DB_NAME
      port: ${DB_PORT:-5432}

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