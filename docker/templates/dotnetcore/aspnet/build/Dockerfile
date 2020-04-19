ARG TAG
FROM mcr.microsoft.com/dotnet/core/sdk:$TAG

#ARG BASE_URL
#ENV ASPNETCORE_URLS http://${BASE_URL}
EXPOSE 5000

COPY entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
WORKDIR /app
ENTRYPOINT ["/docker-entrypoint.sh"]
