# DataOne RDF Graph Service

This project contains relevant files for the pieces of the DataOne RDF Graph service outlined in [../proposal.md](proposal.md).

## get_new_datasets.py

This script queries the DataOne CN for datasets that have been uploaded since the last time the script was run. The scientific metadata for those documents is then cached for processing by the create-graph.py

## create_graph.py

Creates the RDF graph of DataOne datasets
