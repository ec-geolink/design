.PHONY: clean demo

all: clean test

demo:
	python -m demo.demo

test:
	py.test tests

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
