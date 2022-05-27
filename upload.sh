#!/bin/bash

# This script is for CI updates

# Check to see if it has changed
git status --short rfcs/* refs.json | grep -s "M" || exit 0

# setup
git config user.email mnot@mnot.net
git config user.name mnot-bot
git remote set-url --push origin https://mnot:$GITHUB_TOKEN@github.com/mnot/rfc-refs
git checkout -B main origin/master

# Push the changes
git add rfcs/*
git add refs.json
git commit -m "update refs"
git push origin main
