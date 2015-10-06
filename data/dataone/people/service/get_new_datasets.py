"""
    file: get_new_datasets.py
    author: Bryce Meucm

    Gets identifiers, system metadata, and science metadata from the DataOne CN
    which have been uploaded since the provided datetime.
"""

import os
import sys
import datetime
import json
import uuid

from people import processing
from people.formats import eml
from people.formats import dryad
from people.formats import fgdc

from service import settings
from service import dataone
from service import util
from service import dedupe


def main():
    # Settings
    config = util.loadJSONFile('settings.json')

    if 'last_run' not in config:
        print "Last run datetime not found in settings.json. Exiting."
        sys.exit()

    # Create from and to strings
    from_string = config['last_run']
    to_string = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S.0Z")

    # Get document identifiers
    identifiers = dataone.getDocumentIdentifiersSince(from_string, to_string)

    print "Retrieved %d identifiers." % len(identifiers)
    util.continue_or_quit()

    all_records = []

    # Get documents themselves
    for identifier in identifiers[0:1]:
        print "Getting document with identifier `%s`" % identifier

        doc = dataone.getDocument(identifier)
        fmt = processing.detectMetadataFormat(doc)

        if fmt == "eml":
            records = eml.process(doc, identifier)
        elif fmt == "dryad":
            records = dryad.process(doc, identifier)
        elif fmt == "fgdc":
            records = fgdc.process(doc, identifier)
        else:
            print "Unknown format."


        print "Found %d record(s)." % len(records)

        for record in records:
            print json.dumps(record, sort_keys=True, indent=2)

        all_records.append(records)

    deduper = dedupe.Dedupe()
    deduper.register_store("../graph/people_unique.json", 'person', 'json')
    deduper.register_store("../graph/organizations_unique.json", 'organization', 'json')

    for record in records:
        if 'type' not in record:
            continue

        if record['type'] == "person":
            if 'name' not in record and 'email' not in record and len(record['name']) <= 0 and len(record['email']) <= 0:
                key = None
            else:
                key  = "%s#%s" % (record['name'], record['email'])
        elif record['type'] == "organization":
            if 'name' not in record and len(record['name']) <= 0:
                continue

            key  = "%s" % (record['name'])

        print "Looking up %s: %s." % (record['type'], key)

        # De-dupe and integrate records
        found = deduper.find(record['type'], key)

        if found:
            print "Found"

            # Look for a URI
            # If it has one, use it
            # If it doesn't have one, mint one

            if 'uri' in deduper.stores[record['type']][key]:
                print "URI exists"
                print deduper.stores[record['type']][key]['uri']
            else:
                print "Minting URI..."
                uri = str(uuid.uuid4())

                deduper.stores[record['type']][key]['uri'] = uri
                deduper.save_json_store(record['type'])

        else:
            print "Not found"
            # Mint a new URI for it too!
            print "Minting URI"
            uri = str(uuid.uuid4())
            record['uri'] = uri
            deduper.add(record['type'], key, record)


    # Save settings
    # config['last_run'] = to_string
    # util.saveJSONFile(config, 'settings.json')

    return


if __name__ == "__main__":
    main()
