#!/bin/bash

cat - | while read line
do
  updated=`echo $line | awk '{print $2}' | tr -d 'Z' | tr 'T' ' ' | date +"%Y-%m-%dT%H:%M:%S" -f -`
  last1day=`date --utc -d '2 day ago' +"%Y-%m-%dT%H:%M:%S"`

  if [[ "${updated}" < "${last1day}" ]]; then
    echo $line >&2
  fi
done

