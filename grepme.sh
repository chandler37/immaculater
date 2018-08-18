#!/bin/bash

# Greps this directory tree. See also 'git grep'

TOP="$(dirname "$0")"

find "$TOP" -name 'TAGS' -prune -o -name venv -prune -o -name venv3 -prune -o -name clivenv -prune -o -name '.git' -prune -o -name '.coverage' -prune -o -name '.storage' -prune -o -name htmlcov -prune -o -name sitepackages -prune -o -type f -exec egrep '--exclude=*~' '--exclude=.fuse_hidden*' '--exclude=*.bak*' '--exclude=*.pyc' '--exclude=*_pb2.py' -nH -e "$@" {} +
