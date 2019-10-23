# See README.md. TODO(chandler37): Use https://pypi.org/project/flake8-isort/

# /bin/sh is the default; we want bash for consistency with ..
SHELL := $(shell which bash)

ACTIVATE_VENV := source ../venv/bin/activate

.PHONY: all
all: python

.PHONY: sh
sh: python
	$(ACTIVATE_VENV) && ./runme.sh sh $(ARGS)

.PHONY: python
python: protoc_middleman

.PHONY: clean
clean:
	rm -f protoc_middleman pub_installed_middleman brew_installed_middleman protoc_installed_middleman core/pyatdl.pb.cc core/pyatdl.pb.h core/pyatdl_pb2.py generated_javascript_protobufs/core/*.js generated_dart_protobufs/core/*.dart
	rm -f *.pyc **/*.pyc
	rm -fr htmlcov
	rm -f .coverage
	rm -f TAGS
	echo "To be perfectly clean, see 'immaculater reset_database'."

protoc_middleman: core/pyatdl.proto ~/.pub-cache/bin/protoc-gen-dart | protoc_installed_middleman
	protoc --python_out=. $<
	protoc --js_out=import_style=commonjs,binary:generated_javascript_protobufs $<
	protoc "--plugin=protoc-gen-dart=${HOME}/.pub-cache/bin/protoc-gen-dart" --dart_out=generated_dart_protobufs $<
	touch $@

ifeq ($(findstring pub,$(shell type -P pub)),)
pub_installed_middleman: | brew_installed_middleman
	brew update
	brew tap dart-lang/dart
	brew install dart
	touch $@
else
pub_installed_middleman:
	touch $@
endif

ifeq ($(findstring pylint,$(shell type -P pylint)),)
pylint_installed_middleman: | brew_installed_middleman
	brew update
	brew install pylint
	touch $@
else
pylint_installed_middleman:
	touch $@
endif

# See https://developers.google.com/protocol-buffers/docs/pythontutorial
ifeq ($(findstring protoc,$(shell type -P protoc)),)
protoc_installed_middleman: | brew_installed_middleman
	brew update
	brew install protobuf
	touch $@
else
protoc_installed_middleman:
	touch $@
endif

# Homebrew: https://brew.sh/
ifeq ($(findstring brew,$(shell type -P brew)),)
brew_installed_middleman:
	$(error package 'brew' not found so see https://brew.sh/)
else
brew_installed_middleman:
	touch $@
endif

# Note that you could also install from source via
# https://github.com/dart-lang/protobuf/tree/master/protoc_plugin
~/.pub-cache/bin/protoc-gen-dart: | pub_installed_middleman
	pub global activate protoc_plugin

.PHONY: test
test: protoc_middleman
	$(ACTIVATE_VENV) && bash ./testme.sh

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
pylint: protoc_middleman pylint_installed_middleman
	$(ACTIVATE_VENV) && PYTHONPATH=`pwd` pylint --rcfile `pwd`/.pylintrc `find . -name '.git' -prune -o -name '*_pb2.py' -prune -o -type f -name '*.py' -print`

# flake8 is run via ../Makfile's 'make test'

.DEFAULT_GOAL := all
