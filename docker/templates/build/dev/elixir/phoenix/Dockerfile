ARG TAG
FROM elixir:$TAG

# packages
RUN apk update \
    && apk add --no-cache postgresql-client inotify-tools \
    && rm -rf /var/cache/apk/*

# env
ARG USERID
ARG GROUPID
RUN addgroup -S --gid $GROUPID phoenix && adduser -S -D --uid $USERID -G phoenix phoenix
RUN mkdir /app && chown phoenix.phoenix /app
USER phoenix
WORKDIR /app

# phoenix
RUN mix local.hex --force && mix archive.install hex phx_new --force && mix local.rebar --force

# finalize
ADD entrypoint.sh /docker-entrypoint.sh
EXPOSE 4000
CMD ["/docker-entrypoint.sh"]
