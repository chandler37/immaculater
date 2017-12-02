#!/bin/bash
make || exit 1
TOP="$(dirname "$0")"
export PYTHONPATH=".."
rm -f .coverage || exit 1
for x in `find "$TOP" -name '*_test.py' -print`; do
    coverage run -a "$x"
done && \
coverage html -i && \
echo "See directory htmlcov/ and see http://nedbatchelder.com/code/coverage"
