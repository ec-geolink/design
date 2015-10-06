all: dump prune unique graph clean

dump: dump.py
	python dump.py
	wc -l people_dump.csv
	wc -l organizations_dump.csv

prune:
	python prune.py people_dump.csv people
	wc -l people_pruned.csv
	wc -l people_pruned_rejected.csv

	python prune.py organizations_dump.csv organizations
	wc -l organizations_pruned.csv
	wc -l organizations_pruned_rejected.csv

unique:
	python unique.py people_pruned.csv people
	python unique.py organizations_pruned.csv organizations

graph:
	python graph.py

clean:
	find ../ -name '*.pyc' -exec rm -f {} +
	find ../ -name '*.pyo' -exec rm -f {} +
	find ../ -name '*~' -exec rm -f {} +
