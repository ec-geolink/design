.PHONY: clean-pyc demo

all: clean-pyc test

demo:
	python ./demo/demo.py

test:
	py.test tests

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
