.PHONY: clean-pyc demo

all: clean-pyc test

test:
	py.test tests

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
