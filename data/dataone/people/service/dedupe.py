""" dedupe.py

    Functions related to de-duplicating records.
    Information suitable for deduping is stored in database (here, a JSON file).
"""

import json
import os
import uuid


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
            store_length = len(self.stores[kind])

            if kind == 'person':
                store_length += len(self.stores[kind]['unmatched']) - 1

            print "JSON Store registered with key %s. %d records loaded." % (kind, store_length)

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


    def add(self, record):
        """
        Add the record to its appropriate store, if one exists.
        This method also mints URIs at the time of adding.
        Saves the store to disk after adding.
        """

        if 'type' not in record:
            raise Exception("Record was passed to find() that did not have a type.")

        kind = record['type']

        if kind not in self.stores:
            print "Invalid store type: %s." % kind
            return

        key = self.get_key(record)

        if key is None:
            if kind == "organization":
                self.stores[kind]['asdf']
            elif kind == "people":
                self.stores[kind]['unmatched'].append({'records': record, 'uri': self.mint_uri()})
        else:
            if key not in self.stores[kind]:
                self.stores[kind][key] = {}

            if 'records' not in self.stores[kind][key]:
                self.stores[kind][key]['records'] = []

            # Add (and save) record to store (and storefile)
            self.stores[kind][key]['records'].append(record)

            # Mint a URI if necessary
            if 'uri' not in self.stores[kind][key]:
                self.stores[kind][key]['uri'] = self.mint_uri()

        self.save_json_store(kind)


    def find(self, record):
        """
        Find record in its appropriate store.

        Returns True/False
        """

        if 'type' not in record:
            raise Exception("Record was passed to find() that did not have a type.")

        kind = record['type']

        if kind not in self.stores:
            raise Exception("Store '%s' not found." % kind)

        key = self.get_key(record)

        if key is None or key not in self.stores[kind]:
            return False

        # Run the query
        if key in self.stores[kind]:
            return True
        else:
            return False


    def get_key(self, record):
        """
        Generates a key (or None if invalid record) for deduplicating the
        record.
        """

        key = None

        if 'type' not in record:
            return key

        if record['type'] == "person":
            if 'last_name' in record and 'email' in record and len(record['last_name']) > 0 and len(record['email']) > 0:
                key  = "%s#%s" % (record['last_name'], record['email'])
        elif record['type'] == "organization":
            if 'name' in record and len(record['name']) > 0:
                key  = "%s" % (record['name'])

        return key


    def mint_uri(self):
        return str(uuid.uuid4())


    def get_uri(self, record):
        """
        Gets the URI for a given record or returns None if either the record
        has no key or if it doesn't have a URI
        """

        if 'type' not in record:
            return None

        kind = record['type']

        if kind not in self.stores:
            raise Exception("Store of kind %s not found." % kind)

        key = self.get_key(record)

        if key is None:
            return None

        if key not in self.stores[kind]:
            return None

        if 'uri' not in self.stores[kind][key]:
            return None

        return self.stores[kind][key]['uri']
