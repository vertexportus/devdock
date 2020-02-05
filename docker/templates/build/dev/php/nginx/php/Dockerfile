ARG TAG
FROM php:$TAG

# dependencies
ARG APK_DEPS=""
RUN set -x \
    && apk --update --no-cache add $APK_DEPS \
    && apk add --no-cache --virtual .phpize-deps $PHPIZE_DEPS shadow

# user/group
ARG USERID
ARG GROUPID
RUN usermod -u $USERID www-data
RUN groupmod -g $GROUPID www-data
#RUN addgroup -S --gid $GROUPID php && adduser -S -D --uid $USERID -G php php

# extensions
ARG PHP_EXT="none"
ARG PECL_EXT="none"
RUN set -x && if ! [ "$PHP_EXT" = "none" ]; then docker-php-ext-install $PHP_EXT; fi
RUN set -x && if ! [ "$PECL_EXT" = "none" ]; then pecl install $PECL_EXT && docker-php-ext-enable $PECL_EXT; fi

# xdebug
ARG XDEBUG_ENABLE=0
ARG XDEBUG_IDEKEY
ARG XDEBUG_REMOTE_HOST
ARG XDEBUG_REMOTE_PORT
ARG XDEBUG_VERSION
ARG XDEBUG_CONFIG="\nxdebug.remote_enable=1\nxdebug.remote_host=${XDEBUG_REMOTE_HOST}\nxdebug.remote_port=${XDEBUG_REMOTE_PORT}\nxdebug.remote_autostart=1\nxdebug.idekey=${XDEBUG_IDEKEY}\n"
RUN set -x && if [ $XDEBUG_ENABLE -ne 0 ]; then pecl install xdebug-${XDEBUG_VERSION} && docker-php-ext-enable xdebug; else echo "xdebug not installed/configured"; fi
RUN set -x && if [ $XDEBUG_ENABLE -ne 0 ]; then echo -e $XDEBUG_CONFIG >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini; fi

# cleanup
RUN set -x && apk del .phpize-deps

# finalize and run
#USER php
WORKDIR /var/www
EXPOSE 9000
CMD ["php-fpm"]
