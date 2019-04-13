# See README.md.

.PHONY: all
all: python

.PHONY: sh
sh: python
	./runme.sh sh

.PHONY: python
python: protoc_middleman

.PHONY: clean
clean:
	rm -f protoc_middleman core/pyatdl.pb.cc core/pyatdl.pb.h core/pyatdl_pb2.py
	rm -f *.pyc **/*.pyc
	rm -fr htmlcov
	rm -f .coverage
	rm -f TAGS
	echo "To be perfectly clean, see 'immaculater reset_database'."

# protoc is from https://developers.google.com/protocol-buffers/docs/pythontutorial TODO(chandler37): Generate Dart code too using https://github.com/dart-lang/protobuf/tree/master/protoc_plugin and https://developers.google.com/protocol-buffers/docs/reference/dart-generated
protoc_middleman: core/pyatdl.proto
	protoc --python_out=. core/pyatdl.proto
	protoc --js_out=import_style=commonjs,binary:generated_javascript_protobufs core/pyatdl.proto
	@touch $@

.PHONY: test
test: protoc_middleman
	bash ./testme.sh

# See http://nedbatchelder.com/code/coverage:
.PHONY: cov
cov: clean protoc_middleman
	bash ./run_coverage.sh

# See http://pychecker.sourceforge.net/:
.PHONY: pychecker
pychecker: protoc_middleman
	PYTHONPATH=`pwd` pychecker -q `find . -name '.git' -prune -o -type f -name '*.py' -print`

# TODO(chandler): Run pylint against ../todo/...
#
# pylint 1.4.0 was full of bugs; 1.2.0 and 1.6.4 worked. See http://www.pylint.org/:
.PHONY: pylint
pylint: protoc_middleman
	PYTHONPATH=`cd .. && pwd` pylint --rcfile `pwd`/.pylintrc `find . -name '.git' -prune -o -name '*_pb2.py' -prune -o -type f -name '*.py' -print`

# flake8 is run via ../Makfile's 'make test'

# TAGS is not phony but we want 'make TAGS' to generate a new TAGS file each
# time.
.PHONY: TAGS
TAGS:
	ctags -e -R

.DEFAULT_GOAL := all
