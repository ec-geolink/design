all: dedupe

dump: dump.py
	python dump.py

prune: people_dump.csv
	python prune.py people_dump.csv people
	python prune.py organizations_dump.csv organizations

unique: people_dump.csv people_pruned.csv organizations_pruned.csv organizations_dump.csv
	python unique.py people_pruned.csv people
	python unique.py organizations_pruned.csv organizations

graph: people_dump.csv people_pruned.csv people_unique.csv people_unique.json organizations_dump.csv organizations_pruned.csv organizations_unique.csv organizations_unique.json
	python graph.py

clean:
	find ../ -name '*.pyc' -exec rm -f {} +
	find ../ -name '*.pyo' -exec rm -f {} +
	find ../ -name '*~' -exec rm -f {} +
