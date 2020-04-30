#!/bin/bash

code=0

while read line
do
  updated=`echo $line | awk '{print $2}' | tr -d 'Z' | tr 'T' ' ' | date +"%Y-%m-%dT%H:%M:%S" -f -`
  last2day=`date --utc -d '2 day ago' +"%Y-%m-%dT%H:%M:%S"`

  if [[ "${updated}" < "${last2day}" ]]; then
    echo $line >&2
    code=1
  fi
done < <(cat -)

exit ${code}
