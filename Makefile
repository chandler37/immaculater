# See README.md.

.PHONY: all clean distclean test cov pylint pychecker loc sh local pipinstall

all:
	@echo "See README.md"

venv:
	@echo "Install virtualenv system-wide via 'pip3 install virtualenv' if the following fails:"
	virtualenv -p python3 venv
	@echo "Now run the following:"
	@echo "source venv/bin/activate"

pipinstall: venv
	@./ensure_virtualenv.sh || exit 1
	echo proceed
	pip3 install -r requirements.txt
	pip3 install -r requirements-test.txt

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

# TODO(chandler37): flake8 support

# TODO(chandler37): This misses django code?
loc: 
	cd pyatdllib && make loc
