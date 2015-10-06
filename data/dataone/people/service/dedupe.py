""" dedupe.py

    Functions related to de-duplicating records.
    Information suitable for deduping is stored in database (here, a JSON file).
"""

import json
import os


class Dedupe:
    def __init__(self):
        """
        Sets aside a Dictionary of key-value stores.
        """

        self.stores = {}
        self.store_filepaths = {}


    def register_store(self, store, kind, format):
        """
        Registers a key-value store that can be used for deduplicating records.

        Arguments:

            store: Filename to a fiel capable of becoming a key-value store

                e.g. '../mystore.json'

            kind: Key the store will be referenced by

                e.g. 'people'

            format: Type of file referenced by the store parameter

                e.g. 'json'

        No return value.
        """

        if store is None:
            print "Argument `store` must be specified."
            return

        if kind is None:
            print "Argument `kind` (e.g., 'people') must be specified."
            return

        if format is None:
            print "Argument `format` (e.g., 'json') must be specified."
            return

        if format == "json":
            self.load_json_store(store, kind)
        else:
            print "No storetype specified. No default exists. Exiting."


    def load_json_store(self, store, kind):
        """
        Loads a JSON store located at the file path `store` that will be referenced
        by `kind`.

        No return value.
        """

        if not os.path.isfile(store):
            print "Couldn't find file located at %s. Store not registered." % store
            return

        with open(store, "rb") as f:
            self.stores[kind] = json.loads(f.read())
            print "JSON Store registered with key %s. %d keys loaded." % (kind, len(self.stores[kind]))

        self.store_filepaths[kind] = store


    def save_json_store(self, kind):
        """
        Save a JSON store to disk.
        """

        if kind not in self.store_filepaths:
            print "Store filepath not found for store %s." % store

        if kind not in self.stores:
            print "Store %s not found." % store

        with open(self.store_filepaths[kind], "wb") as f:
            json.dump(self.stores[kind], f)


    def add(self, kind, key, record):
        """
        Add the record to the `kind` store at key `key`
        """

        if kind not in self.stores:
            print "Invalid store type: %s." % kind
            return

        if key is None:
            self.stores[kind]['unmatched'].append({'records': record})
        else:
            if key not in self.stores[kind]:
                print "Initializing key %s in %s." % (key, kind)
                self.stores[kind][key] = {}

            if 'records' not in self.stores[kind][key]:
                print "For some odd reason this key has no 'records' key."
                self.stores[kind][key]['records'] = []

            # Add (and save) record to store (and storefile)
            self.stores[kind][key]['records'].append(record)

        self.save_json_store(kind)


    def find(self, kind, key):
        """
        Find `key` in the key-value store with the key `kind`.

        Returns True/False
        """


        if kind not in self.stores:
            raise Exception("Store '%s' not found." % kind)

        if key not in self.stores[kind]:
            return False

        # Get a reference to the store
        store_records = self.stores[kind][key]['records']

        # Run the query
        if key in store_records:
            return True
        else:
            return False
