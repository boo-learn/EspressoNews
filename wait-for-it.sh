#!/bin/bash
# wait-for-it.sh

set -e

host="$1"
shift
cmd="$@"

while true; do
  if curl --output /dev/null --head --fail "$host"; then
    >&2 echo "Service is down - executing command"
    exec $cmd
  else
    ret=$?
    if [ $ret -eq 7 ]; then
      >&2 echo "Service is available - sleeping"
      sleep 1
    else
      >&2 echo "Service is down - executing command"
      exec $cmd
    fi
  fi
done
