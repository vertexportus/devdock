# devdock
Set of tools to help manage a docker-oriented development environment

## new project

create a new folder, add a `project.yaml` file on it. Example:

```yaml
devdock:
  github: vertexportus/devdock.git

projects:
  laravel:
    github: username/laravel.git
    services:
      api:
        github: username/apiproject.git
        services:
          api:
            template: php.laravel.nginx
            database: db
            env_files: true
            ports: true
      frontend:
        github: vertexportus/frontendproject.git
        services:
          frontend:
            template: node.angular

services:
  db:
    template: postgres
```

run command:
```bash
rq config init
```

you can change enviroment variables on the `.env` file

to start the containers, you can run docker up with generation:

```bash
rq docker up --generate
```

## TODO

- add support for angular commands through cli
- add support for dynamic nginx.proxy
- change default ports for http/https