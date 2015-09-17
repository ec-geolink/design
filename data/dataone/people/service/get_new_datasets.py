"""
    file: get_new_datasets.py
    author: Bryce Meucm

    Gets identifiers, system metadata, and science metadata from the DataOne CN
    which have been uploaded since the provided datetime.
"""

import os
import sys
import datetime

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

    # Get documents
    documents = dataone.getDocumentIdentifiersSince(from_string, to_string)

    print "Retreived %d identifiers." % len(documents)
    util.continue_or_quit()

    config['last_run'] = to_string

    # Save settings
    settings.saveSettings(config, 'settings.json')

    return


if __name__ == "__main__":
    main()
