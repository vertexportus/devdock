#!bin/sh

echo SMEE_PROXY_URL=$SMEE_PROXY_URL
echo SMEE_TARGET_URL=$SMEE_TARGET_URL
smee -u $SMEE_PROXY_URL -t $SMEE_TARGET_URL
