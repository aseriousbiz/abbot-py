#!/usr/bin/env sh

set -e

if [ -z $1 ]; then
  echo "Runner cannot be empty!"
  exit 1
fi

if [ -z $2 ]; then
  echo "Tag cannot be empty!"
  exit 1
fi

curl -X POST https://api.github.com/repos/aseriousbiz/docker/actions/workflows/12816714/dispatches \
-H "Content-Type: application/json" -H 'Accept: application/vnd.github.everest-preview+json' \
-H "Authorization: token ${GH_BOT_TOKEN}" \
--data "{ \"ref\": \"main\", \"inputs\": {\"runner\": \"$1\", \"tag\": \"$2\"} }"
