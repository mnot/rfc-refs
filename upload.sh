#!/bin/bash

# This script is for CI updates

# Check to see if it has changed
git diff --quiet -- rfcs/ refs.json && exit 0
if [ "$(git diff --raw | cut -f2)" = "rfcs/rfc-index.txt" ] && [ "$(git diff -U0 | grep '@@')" = "@@ -8 +8 @@" ]; then
    exit 0
fi

# setup
git config --local user.email mnot@mnot.net
git config --local user.name mnot-bot

# Push the changes
git add -- rfcs/ refs.json
git commit -m "update refs"
git push
