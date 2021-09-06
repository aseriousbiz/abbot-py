#!/usr/bin/env sh

set -e

if [ -z $1 ]; then
  echo "Runner cannot be empty!"
  exit 1
fi

if [ -z $2 ]; then
  echo "Source tag cannot be empty!"
  exit 1
fi

if [ -z $3 ]; then
  echo "Target tag cannot be empty!"
  exit 1
fi

curl -X POST https://api.github.com/repos/aseriousbiz/docker/actions/workflows/12887088/dispatches \
-H "Content-Type: application/json" -H 'Accept: application/vnd.github.everest-preview+json' \
-H "Authorization: token ${GH_BOT_TOKEN}" \
--data "{ \"ref\": \"main\", \"inputs\": {\"runner\": \"$1\", \"source_tag\": \"$2\", \"target_tag\": \"$3\" } }"
