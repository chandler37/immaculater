# If you have difficulty with this Makefile, you might install the latest GNU
# Make via Homebrew (https://brew.sh/) [try `brew install make`] and try again
# using `gmake`. If that doesn't work you might want to install the latest bash
# via `brew install bash` and update your PATH to prefer it over the older
# MacOS-provided bash.

# /bin/sh is the default; we want bash so we can 'source venv/bin/activate':
SHELL := $(shell which bash)

ACTIVATE_VENV := source venv/bin/activate

.PHONY: help
help:
	@echo "See README.md but maybe... make test"

# One-time installation of heroku CLI globally.
.PHONY: install_tools
install_tools:
	@echo "If brew is not found, you need to install Homebrew; see https://brew.sh/"
	brew update
	brew tap heroku/brew
	brew install heroku

PYTHON := python3
PYTHON_INSTALLED := $(shell command -v $(PYTHON) 2> /dev/null)

PIP := pip -q

venv:
ifndef PYTHON_INSTALLED
	$(error "$(PYTHON) is not available please install it with Homebrew via 'brew install python' or with pyenv")
endif
	cat runtime.txt | grep --silent "\\b3\\.7\\.10\\b" || { echo "You changed the heroku python runtime version and you must now edit the Makefile to match it."; exit 1; }
	$(PYTHON) --version | grep --silent "\\b3\\.7\\.10\\b" || { echo "You must use python 3.7.10; you might want Homebrew or pyenv to install that."; exit 1; }
	$(PYTHON) -m venv venv
	$(ACTIVATE_VENV) && pip -q install --upgrade pip
	$(ACTIVATE_VENV) && cd venv && git clone --quiet --depth 1 --recurse-submodules "https://github.com/chandler37/pytest-mypy.git" && cd pytest-mypy && $(PIP) install -c ../../requirements.txt -c ../../requirements-test.txt --upgrade .
	@echo "The virtualenv is not active unless you run the following:"
	@echo "$(ACTIVATE_VENV)"
	@echo ""
	@echo "But if you use the Makefile it activates it for you temporarily."

.PHONY: pipinstall
pipinstall: venv/requirements-test-installed-by-makefile

venv/requirements-test-installed-by-makefile: requirements-test.txt requirements.txt | venv
	$(ACTIVATE_VENV) && $(PIP) install -r $<
	echo "Now let's make sure that every dependency, transitive or direct, has a version pinned in" $^
	diff <(cat $^ | grep -v -e '^-r requirements.txt$$' | sort -f) \
	     <($(ACTIVATE_VENV) \
	       && $(PIP) freeze \
			| grep -v '^pytest-mypy @ file://.*/pytest-mypy$$' \
			| sort -f)
	touch $@

.PHONY: pipdeptree
pipdeptree: venv/requirements-test-installed-by-makefile
	$(ACTIVATE_VENV) && ./venv/bin/pipdeptree

venv/local-migrations-performed: todo/migrations/*.py | venv/requirements-test-installed-by-makefile venv/protoc-has-run
	$(ACTIVATE_VENV) && python manage.py migrate
	touch $@

.PHONY: localmigrate
localmigrate: venv/local-migrations-performed
	$(ACTIVATE_VENV) && python manage.py migrate

.PHONY: localsuperuser
localsuperuser: venv/local-migrations-performed
	$(ACTIVATE_VENV) && python manage.py createsuperuser

.PHONY: web
web: local

.PHONY: local
local: venv/local-migrations-performed
	$(ACTIVATE_VENV) && DJANGO_DEBUG=True python manage.py runserver -v 3 5000

venv/protoc-has-run:
	cd pyatdllib && $(MAKE) protoc_middleman
	touch $@

.PHONY: sh shell
shell sh: venv/local-migrations-performed venv/protoc-has-run
	cd pyatdllib && $(MAKE) sh ARGS="$(ARGS)"

.PHONY: djsh djshell
djshell djsh: venv/requirements-test-installed-by-makefile
	$(ACTIVATE_VENV) && DJANGO_DEBUG=True python manage.py shell

.PHONY: clean
clean: distclean

# You need protoc (Google's protobuf compiler) to regenerate *_pb2.py
#
# TODO: 'make clean' prints out 'To be perfectly clean, see 'immaculater reset_database'.'
.PHONY: distclean
distclean:
	cd pyatdllib && $(MAKE) clean
	rm -f db.sqlite3 .coverage django.log pyatdllib/core/pyatdl_pb2.pyi
	rm -fr venv htmlcov .pytest_cache .mypy_cache
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	@echo "Print deactivate your virtual environment if you manually activated it (unlikely because the Makefile does it for you). Exit the shell if you do not know how."

PYTEST_MARK :=
# TODO(chandler37): convert unittest tests to pytest
#
# NOTE: The following runs just mypy: --mypy -m mypy
PYTEST_MYPY := --mypy
PYTEST_ARGS := todo/tests
PYTESTLIB_ARGS := pyatdllib/
PYTEST_FLAGS := --cov=todo --cov=pyatdllib --cov-report=html -s -vv
# Usually useful PYTEST_FLAGS additions are `-vv -s`, which make things verbose.
PYTEST_CMD := DJANGO_DEBUG=True python -m pytest $(PYTEST_MARK) $(PYTEST_MYPY) $(PYTEST_FLAGS)

.PHONY: flake8
flake8:
	$(ACTIVATE_VENV) && python -m flake8 immaculater todo pyatdllib

.PHONY: lint
lint:
	$(MAKE) flake8

.PHONY: mypy
mypy:
	$(MAKE) -k pytest pytestlib PYTEST_MYPY="--mypy -m mypy"

.PHONY: pytest
pytest:
	cd pyatdllib && $(MAKE) protoc_middleman
	$(ACTIVATE_VENV) && $(PYTEST_CMD) $(PYTEST_ARGS)

# TODO(chandler37): The following only runs mypy; we need to tell pytest how to
# collect all the old-style tests, or we need to convert them to new-style
# pytest test cases. Consider something like "cd pyatdllib && find . -name
# '*_test.py' -print0 | xargs -0 echo python -m pytest"
.PHONY: pytestlib
pytestlib: venv/requirements-test-installed-by-makefile
	cd pyatdllib && $(MAKE) protoc_middleman
	$(ACTIVATE_VENV) && $(PYTEST_CMD) $(PYTESTLIB_ARGS)

# test and run the flake8 linter
.PHONY: test
test: venv/requirements-test-installed-by-makefile
	$(MAKE) pytest
	$(MAKE) pytestlib
	cd pyatdllib && $(MAKE) test
	$(MAKE) flake8
	@echo ""
	@echo "Tests and linters passed".

.PHONY: testlib
testlib: venv/requirements-installed-by-makefile venv/requirements-test-installed-by-makefile
	cd pyatdllib/ && $(MAKE) protoc_middleman && PYTHONPATH=$$(pwd) ../venv/bin/py.test $(PYTEST_MARK) $(PYTEST_FLAGS) $(PYTEST_ARGS)

.PHONY: upgrade
upgrade: unfreezeplus pipinstall test
	@echo "See the 'Upgrading Third-Party Dependencies' section of ./README.md"

# It's a best practice to run 'make clean' before 'make unfreezeplus'.
.PHONY: unfreezeplus
unfreezeplus: venv/local-migrations-performed
	@git diff-index --quiet HEAD || { echo "not in a clean git workspace; run 'git status'"; exit 1; }
	rm -f venv/requirements-test-installed-by-makefile
	# If this fails, `deactivate; make distclean` and try again:
	$(ACTIVATE_VENV) \
		&& $(PIP) freeze \
			| sed -e "s/ @.*//" \
			| xargs $(PIP) uninstall -y
	sed -i "" -e "s/=.*//" requirements-test.txt
	sed -i "" -e "s/=.*//" requirements.txt
	sed -i "" -e "s/Django/Django<3.0.0/" requirements.txt
	$(ACTIVATE_VENV) && $(PIP) install -r requirements.txt
	$(ACTIVATE_VENV) && $(PIP) freeze > requirements.txt
	$(ACTIVATE_VENV) && $(PIP) install -r requirements-test.txt
	comm -i -3 requirements.txt <($(ACTIVATE_VENV) && $(PIP) freeze) | sed -e 's/^[[:blank:]]*//' > requirements-test.txt
	cat <(echo "-r requirements.txt") requirements-test.txt > requirements-test.txt.tmp && mv requirements-test.txt.tmp requirements-test.txt
	git diff-index --quiet HEAD || { echo "Let us try these versions..."; $(MAKE) clean test && echo "" && echo "Tests pass. Be wary of major version bumps."; }

.PHONY: cov
cov: venv
	@echo "We produce two htmlcov directories, one in the root directory for the pytest tests for the Django app, and one in pyatdllib for the other tests."
	cd pyatdllib && $(MAKE) protoc_middleman
	$(ACTIVATE_VENV) && DJANGO_DEBUG=True python ./run_django_tests.py $(ARGS)
	cd pyatdllib && $(MAKE) cov
	@echo "Try this: open htmlcov/index.html; open pyatdllib/htmlcov/index.html"


.PHONY: pychecker
pychecker: venv
	cd pyatdllib && $(MAKE) pychecker

.PHONY: pylint
pylint: venv
	cd pyatdllib && $(MAKE) pylint

# counts lines of code
.PHONY: dilbert
dilbert:
	wc -l `find todo immaculater pyatdllib -name '.git' -prune -o -name '*_pb2.py' -prune -o -name '*_pb.js' -prune -o -type f -name '*.py' -print` pyatdllib/core/pyatdl.proto todo/templates/*.html immaculater/static/immaculater/*.js

.PHONY: papertrail
papertrail:
	@echo "Install heroku system-wide via 'make install_tools' if the following fails:"
	heroku "addons:open" papertrail

.PHONY: mainton
mainton:
	@echo "Install heroku system-wide via 'make install_tools' if the following fails:"
	heroku "maintenance:on"

.PHONY: maintoff
maintoff:
	@echo "Install heroku system-wide via 'make install_tools' if the following fails:"
	heroku "maintenance:off"

.PHONY: pushbranch
pushbranch:
	git push origin HEAD

.DEFAULT_GOAL := help
