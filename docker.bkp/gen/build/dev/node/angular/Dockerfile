ARG TAG
FROM node:$TAG

# install deps
ARG ANGULAR_VERSION
RUN set -x && npm install -g @angular/cli@$ANGULAR_VERSION

# set user/group
RUN set -x && apk add --update --no-cache --virtual .shadow shadow
ARG USERID
ARG GROUPID
RUN usermod -u $USERID node
RUN groupmod -g $GROUPID node
RUN set -x && apk del .shadow
USER node

# set envs
ENV PATH /app/node_modules/.bin:$PATH

# finalize and run
WORKDIR /app
EXPOSE 4200
CMD ["sh", "-c", "ng serve --public-host $BASE_URL --host 0.0.0.0"]