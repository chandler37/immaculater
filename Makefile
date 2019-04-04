# See README.md.

.PHONY: all clean distclean test cov pylint pychecker loc sh local pipinstall pipdeptree localmigrate localsuperuser

all:
	@echo "See README.md"

localmigrate:
	@./ensure_virtualenv.sh || exit 1
	python manage.py migrate

localsuperuser:
	@./ensure_virtualenv.sh || exit 1
	python manage.py createsuperuser

venv:
	@echo "Install virtualenv system-wide via 'pip3 install virtualenv' if the following fails:"
	virtualenv -p python3 venv
	@echo "Now run the following:"
	@echo "source venv/bin/activate"

pipinstall: venv
	@./ensure_virtualenv.sh || exit 1
	pip3 install -r requirements.txt
	pip3 install -r requirements-test.txt

venv/bin/pipdeptree: venv
	@./ensure_virtualenv.sh || exit 1
	pip3 install pipdeptree

pipdeptree: venv/bin/pipdeptree
	@./ensure_virtualenv.sh || exit 1
	./venv/bin/pipdeptree

local: venv
	@./ensure_virtualenv.sh || exit 1
	DJANGO_DEBUG=True python manage.py runserver 5000

sh: venv
	@./ensure_virtualenv.sh || exit 1
	cd pyatdllib && make sh

clean:
	cd pyatdllib && make clean
	rm -f *.pyc **/*.pyc

distclean:
	make clean
	rm -fr venv
	@echo "Print deactivate your virtualenv. Exit the shell if you do not know how."

# test and run the flake8 linter:
test: venv
	@./ensure_virtualenv.sh || exit 1
	cd pyatdllib && make test
	python ./run_django_tests.py

cov: venv
	cd pyatdllib && make cov

pychecker: venv
	cd pyatdllib && make pychecker

pylint: venv
	cd pyatdllib && make pylint

# TODO(chandler37): This misses django code?
loc: 
	cd pyatdllib && make loc
