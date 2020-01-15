# devdock
Set of tools to help manage a docker-oriented development environment

## temp example

```
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