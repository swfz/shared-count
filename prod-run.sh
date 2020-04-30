#!/bin/bash

url=$1
service=$2

json=`cat <<EOS
{
  "url": "${url}",
  "service": "${service}"
}
EOS
`

echo ${json}

gcloud pubsub topics publish memo-collector-${service} --message "${json}"
