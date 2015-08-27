.PHONY: clean link

all: clean test

link:
	python -m link.link

test:
	py.test tests

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
