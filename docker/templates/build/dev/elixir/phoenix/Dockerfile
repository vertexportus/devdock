ARG TAG

FROM elixir:$TAG

ARG TAG
RUN echo "building image from elixir:$TAG"

# packages
RUN apk update \
    && apk add --no-cache postgresql-client inotify-tools \
    && rm -rf /var/cache/apk/*

# env
ARG USERID
ARG GROUPID
RUN echo "uid=$USERID and gid=$GROUPID"
RUN addgroup -S --gid $GROUPID phoenix && adduser -S -D --uid $USERID -G phoenix phoenix
RUN mkdir /app && chown phoenix.phoenix /app
USER phoenix
WORKDIR /app

# phoenix
RUN mix local.hex --force && mix archive.install hex phx_new --force && mix local.rebar --force

# finalize
EXPOSE 4000
CMD ["iex"]
