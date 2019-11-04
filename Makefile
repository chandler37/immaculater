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

# One-time installation of virtualenv and heroku CLI globally.
#
# We use `pip3`, not `pip`. On MacOS `pip` is Python 2.7 (either
# via Homebrew `python@2` or, frigteningly, the stock Python provided by
# Apple), not Python 3. `pip3` (using python version 3) is courtesy of the
# `python` package from [Homebrew](https://brew.sh/).
.PHONY: install_tools
install_tools:
	@echo "If brew is not found, you need to install Homebrew; see https://brew.sh/"
	brew update
	brew install python
	pip3 install virtualenv
	brew tap heroku/brew && brew install heroku

venv:
	@echo "Install virtualenv system-wide via 'make install_tools' if the following fails:"
	virtualenv -p python3 venv
	@echo "The virtualenv is not active unless you run the following:"
	@echo "source venv/bin/activate"
	@echo ""
	@echo "But if you use the Makefile it activates it for you temporarily."

.PHONY: pipinstall
pipinstall: venv/requirements-installed-by-makefile venv/requirements-test-installed-by-makefile

venv/requirements-installed-by-makefile: requirements.txt | venv
	$(ACTIVATE_VENV) && pip3 install -r $<
	touch $@

venv/requirements-test-installed-by-makefile: requirements-test.txt | venv
	$(ACTIVATE_VENV) && pip3 install -r $<
	touch $@

venv/bin/pipdeptree: venv
	$(ACTIVATE_VENV) && pip3 install pipdeptree

.PHONY: pipdeptree
pipdeptree: venv/bin/pipdeptree venv/requirements-installed-by-makefile
	$(ACTIVATE_VENV) && ./venv/bin/pipdeptree

venv/local-migrations-performed: todo/migrations/*.py | venv/requirements-installed-by-makefile venv/protoc-has-run
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
	$(ACTIVATE_VENV) && DJANGO_DEBUG=True python manage.py runserver 5000

venv/protoc-has-run:
	cd pyatdllib && make protoc_middleman
	touch $@

.PHONY: sh shell
shell sh: venv/local-migrations-performed venv/protoc-has-run
	cd pyatdllib && make sh ARGS="$(ARGS)"

.PHONY: djsh djshell
djshell djsh: venv/requirements-installed-by-makefile venv/requirements-test-installed-by-makefile
	$(ACTIVATE_VENV) && DJANGO_DEBUG=True python manage.py shell

.PHONY: clean
clean: distclean

# You need protoc (Google's protobuf compiler) to regenerate *_pb2.py
#
# TODO: 'make clean' prints out 'To be perfectly clean, see 'immaculater reset_database'.'
.PHONY: distclean
distclean:
	rm -f *.pyc **/*.pyc
	cd pyatdllib && make clean
	rm -f db.sqlite3 .coverage
	rm -fr venv htmlcov
	@echo "Print deactivate your virtualenv if you manually activated it (unlikely because the Makefile does it for you). Exit the shell if you do not know how."

# test and run the flake8 linter (unless ARGS is --nolint):
.PHONY: test
test: venv/requirements-installed-by-makefile venv/requirements-test-installed-by-makefile
	cd pyatdllib && make protoc_middleman
	$(ACTIVATE_VENV) && DJANGO_DEBUG=True python ./run_django_tests.py $(ARGS)
	cd pyatdllib && make test
	@echo ""
	@echo "Tests and linters passed".

.PHONY: upgrade
upgrade: unfreezeplus pipinstall test
	@echo "See the 'Upgrading Third-Party Dependencies' section of ./README.md"

.PHONY: unfreezeplus
unfreezeplus:
	@git diff-index --quiet HEAD || { echo "not in a clean git workspace; run 'git status'"; exit 1; }
	rm -f venv/requirements-test-installed-by-makefile venv/requirements-installed-by-makefile
	# If this fails, `deactivate; make distclean` and try again:
	$(ACTIVATE_VENV) && pip freeze | xargs pip3 uninstall -y
	$(ACTIVATE_VENV) && sed -i "" -e "s/=.*//" requirements.txt
	$(ACTIVATE_VENV) && pip3 install -r requirements.txt
	$(ACTIVATE_VENV) && pip3 freeze > requirements.txt


.PHONY: cov
cov: venv
	@echo "We produce two htmlcov directories, one in the root directory for the pytest tests for the Django app, and one in pyatdllib for the other tests."
	cd pyatdllib && make protoc_middleman
	$(ACTIVATE_VENV) && DJANGO_DEBUG=True python ./run_django_tests.py $(ARGS)
	cd pyatdllib && make cov
	@echo "Try this: open htmlcov/index.html; open pyatdllib/htmlcov/index.html"


.PHONY: pychecker
pychecker: venv
	cd pyatdllib && make pychecker

.PHONY: pylint
pylint: venv
	cd pyatdllib && make pylint

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
