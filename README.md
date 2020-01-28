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