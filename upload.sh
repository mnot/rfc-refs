#!/bin/bash

# This script is for CI updates

# Check to see if it has changed
git status --short rfcs/* refs.json | grep -s "M" || exit 0
if [ "$(git diff --raw | cut -f2)" = "rfcs/rfc-index.txt" ] && [ "$(git diff -U0 | grep '@@')" = "@@ -8 +8 @@" ]; then
    exit 0
fi

# setup
git config user.email mnot@mnot.net
git config user.name mnot-bot
git remote set-url --push origin https://mnot:$GITHUB_TOKEN@github.com/mnot/rfc-refs
git checkout -B main origin/main

# Push the changes
git add rfcs/*
git add refs.json
git commit -m "update refs"
git push origin main
