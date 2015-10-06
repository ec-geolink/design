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

    deduper = dedupe.Dedupe()
    deduper.register_store("../graph/people_unique.json", 'person', 'json')
    deduper.register_store("../graph/organizations_unique.json", 'organization', 'json')


    # Get documents themselves
    for identifier in identifiers:
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

            # De-dupe and integrate records
            found = deduper.find(record)

            if found:
                print "Found"

                uri = deduper.get_uri(record)

                if uri is not None:
                    print "URI exists and is %s." % uri
                else:
                    print "URI does not exist."
            else:
                print "Record not found."

                deduper.add(record)


    # Save settings
    config['last_run'] = to_string
    util.saveJSONFile(config, 'settings.json')

    return


if __name__ == "__main__":
    main()
