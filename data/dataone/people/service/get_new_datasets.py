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

from people import processing
from people.formats import eml
from people.formats import dryad
from people.formats import fgdc

from service import settings
from service import dataone
from service import util


def main():
    # Settings
    config = settings.initializeSettings('settings.json')

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


    # Get documents themselves
    for identifier in identifiers[0:4]:
        print "Getting document with identifier `%s`" % identifier

        doc = dataone.getDocument(identifier)
        fmt = processing.detectMetadataFormat(doc)

        if fmt == "eml":
            records = eml.process(doc, identifier)
        elif fmt == "dryad":
            records = dryad.process(doc, identifier)
        elif fmt == "fgdc":
            records = fgdc.process(doc, identifier)


        print "Found %d record(s)." % len(records)

        for record in records:
            print json.dumps(record, sort_keys=True, indent=2)


    # Save settings
    # config['last_run'] = to_string
    # settings.saveSettings(config, 'settings.json')

    return


if __name__ == "__main__":
    main()
