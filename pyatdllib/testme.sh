#!/bin/bash

# To test just one test case, do something like this:
# cd $TOP && PYTHONPATH=$TOP python ui/immaculater_test.py ImmaculaterTestCase.testArgProcessing

TOP="$(dirname "$0")"

function die() {
    echo "testme.sh FAILURE" "$@"
    exit 1
}

function testone() {
    PYTHONPATH="$TOP/.." python "$1"
}

function testme() {
    for x in `find "$TOP" -name '*_test.py'`; do
	testone "$x" || die "$x"
    done
    echo "testme.sh SUCCESS"
}

testme
