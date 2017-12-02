#!/bin/bash

TOP="$(dirname "$0")"

cd "$TOP" || exit 1
make || exit 1
PYTHONPATH=".." python -m pyatdllib.ui.immaculater "$@"
