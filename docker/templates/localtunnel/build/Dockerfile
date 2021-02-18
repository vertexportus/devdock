ARG TAG
FROM node:$TAG

RUN yarn global add localtunnel
COPY config/entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
