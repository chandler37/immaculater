# See README.md.

.PHONY: all clean test cov pylint pychecker loc sh local

all:
	@echo "See README.md"

local:
	source venv/bin/activate && DJANGO_DEBUG=True python manage.py runserver 5000

sh:
	cd pyatdllib && make sh

clean:
	cd pyatdllib && make clean
	rm -f *.pyc **/*.pyc

test:
	cd pyatdllib && make test
	python ./run_django_tests.py

cov:
	cd pyatdllib && make cov

pychecker:
	cd pyatdllib && make pychecker

pylint:
	cd pyatdllib && make pylint

loc:
	cd pyatdllib && make loc
