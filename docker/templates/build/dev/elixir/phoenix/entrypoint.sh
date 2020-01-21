#!/bin/sh
# With help from https://dogsnog.blog/2018/02/02/a-docker-based-development-environment-for-elixirphoenix/

set -e
# Wait for Postgres to become available.
export PGPASSWORD="$DB_PASSWORD"
until psql -h $DB_HOST -U "$DB_USERNAME" -c '\q' 2>/dev/null; do
  >&2 echo "Postgres is unavailable at: $DB_USERNAME@$DB_HOST - $?"
  sleep 2
done

mix ecto.create
mix ecto.migrate
mix phx.server
