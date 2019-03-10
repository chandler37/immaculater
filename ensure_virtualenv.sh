#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pip3 -V | grep ' from ' | grep "$DIR" 1>/dev/null || { echo "You must run 'source venv/bin/activate'" 1>&2 ; exit 1; }
exit 0
