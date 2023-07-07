#!/bin/bash
# wait-for-it.sh

set -e

host="$1"
shift
cmd="$@"

sleep 10

while PING=$(ping -c1 $host > /dev/null 2>&1); do
  >&2 echo "Service is available - sleeping"
  sleep 1
done

>&2 echo "Service is down - executing command"
exec $cmd