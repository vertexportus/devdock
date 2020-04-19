ARG TAG
FROM minio/minio:$TAG

COPY config/mc /bin/mc
RUN set -x && chmod +x /bin/mc
