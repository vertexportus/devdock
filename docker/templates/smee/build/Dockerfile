ARG TAG
FROM node:$TAG

RUN yarn global add smee-client
COPY config/entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# ENTRYPOINT ["smee"]
# CMD ["--help"]
ENTRYPOINT ["/docker-entrypoint.sh"]
