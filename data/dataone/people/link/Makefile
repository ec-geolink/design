all: dedupe

dump: dump.py
	python dump.py

prune: people_dump.csv
	python prune.py people_dump.csv people

uniquify: people_dump.csv people_pruned.csv
	python uniquify.py people_pruned.csv people

graph: people_dump.csv people_pruned.csv people_unique.csv people_deduped.json
	python create_graph.py people_deduped.json people

clean:
	find . -name 'people*.csv' -exec rm -f {} +
