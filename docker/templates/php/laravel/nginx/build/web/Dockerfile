ARG TAG
FROM nginx:$TAG

# set user/group
RUN set -x && apk add --update --no-cache --virtual .shadow shadow
ARG USERID
ARG GROUPID
RUN usermod -u $USERID nginx
RUN groupmod -g $GROUPID nginx
RUN set -x && apk del .shadow

# nginx conf
RUN set -x && rm -f /etc/nginx/conf.d/default.conf
COPY config/nginx-php.conf /etc/nginx/conf.d/phpupstream.conf
COPY config/nginx-site.conf /etc/nginx/sites-available/default.conf
COPY config/nginx.conf /etc/nginx/nginx.conf

# SSL
#COPY config/ssl.crt /etc/ssl/certs/selfsigned.crt
#COPY config/ssl.key /etc/ssl/private/selfsigned.key

# finalize and run
WORKDIR /var/www
EXPOSE 80 443
CMD ["nginx"]
