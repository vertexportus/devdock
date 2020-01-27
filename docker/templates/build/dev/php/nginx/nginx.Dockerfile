ARG TAG
FROM nginx:$TAG
ARG TAG
RUN echo "building image from nginx:$TAG"

# nginx conf
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
