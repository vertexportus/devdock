ARG TAG

FROM php:$TAG

ARG TAG
RUN echo "building image from php:$TAG"