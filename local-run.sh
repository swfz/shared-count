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

data=$(echo ${json} | base64 |tr -d '\n')

echo $data

curl -XPOST http://localhost:8080/ -H 'Content-Type:application/json; charset=utf-8' -d @- <<EOS
{
  "data": {
    "data": "${data}"
  }
}
EOS

