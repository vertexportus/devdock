#!bin/sh

echo LOCALTUNNEL_PROXY_LOCAL_HOST=$LOCALTUNNEL_PROXY_LOCAL_HOST
echo LOCALTUNNEL_PROXY_PORT=$LOCALTUNNEL_PROXY_PORT
echo LOCALTUNNEL_SUBDOMAIN=$LOCALTUNNEL_SUBDOMAIN
extra_params=''
if [ -n "$LOCALTUNNEL_SUBDOMAIN" ]; then
  extra_params="--subdomain $LOCALTUNNEL_SUBDOMAIN"
fi
lt --port $LOCALTUNNEL_PROXY_PORT --local-host $LOCALTUNNEL_PROXY_LOCAL_HOST --print-requests $extra_params
