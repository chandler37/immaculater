# See README.md.

# TAGS is not phony but we want 'make TAGS' to generate a new TAGS file each
# time.
.PHONY: all python clean test protoc_middleman cov pylint pychecker loc TAGS sh

all: python

sh: python
	./runme.sh sh

python: protoc_middleman

clean:
	rm -f protoc_middleman core/pyatdl.pb.cc core/pyatdl.pb.h core/pyatdl_pb2.py
	rm -f *.pyc **/*.pyc
	rm -fr htmlcov
	rm -f .coverage
	rm -f TAGS
	echo "To be perfectly clean, see 'immaculater reset_database'."

# protoc is from https://developers.google.com/protocol-buffers/docs/pythontutorial
protoc_middleman: core/pyatdl.proto
	protoc --python_out=. core/pyatdl.proto
	@touch protoc_middleman

test: protoc_middleman
	bash ./testme.sh

# See http://nedbatchelder.com/code/coverage:
cov: clean protoc_middleman
	bash ./run_coverage.sh

# See http://pychecker.sourceforge.net/:
pychecker: protoc_middleman
	PYTHONPATH=`pwd` pychecker -q `find . -name '.git' -prune -o -type f -name '*.py' -print`

# TODO(chandler): Run pylint against ../todo/...
#
# pylint 1.4.0 was full of bugs; 1.2.0 and 1.6.4 worked. See http://www.pylint.org/:
pylint: protoc_middleman
	PYTHONPATH=`cd .. && pwd` pylint --rcfile `pwd`/.pylintrc `find . -name '.git' -prune -o -name '*_pb2.py' -prune -o -type f -name '*.py' -print`

# How many lines of code are there?
loc:
	wc -l `find . -name '.git' -prune -o -name '*_pb2.py' -prune -o -type f -name '*.py' -print` core/pyatdl.proto ../todo/views.py ../todo/templates/*.html ../immaculater/static/immaculater/*.js ../cli/todo.py

TAGS:
	ctags -e -R
