ARG TAG
FROM node:$TAG

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
CMD ["sh", "-c", "ng serve --host 0.0.0.0 --disableHostCheck"]
