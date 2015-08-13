"""
    file: processing.py
    author: Bryce Mecum (mecum@nceas.ucsb.edu)

    Processes the scientific metadata documents in ./documents for person
    and organization information. For each document, the script tries to find
    the person in an existing list. Matches are currently made off of all
    information available but future versions should be more loose about this.

    The document a person/organization was found in are also added to that
    person/organization so the documents belonging to that person/organization
    can be attributed to them and used in later graph generation activities.
"""

import os
import re
import uuid
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

from people.formats import eml


def processDirectory(job):
    filenames = os.listdir("./%s" % job.directory)
    # documents = [f for f in filenames if re.search("scimeta\.xml$", f)]

    for filename in filenames:
        try:
            xmldoc = ET.parse("%s/%s" % (job.directory, filename))
        except ParseError:
            continue

        processDocument(job, xmldoc)


def processDocument(job, xmldoc):
    """ Process an individual document."""
    document = uuid.uuid4()

    root = xmldoc.getroot()

    if re.search("eml$", root.tag):
        eml.process(job, xmldoc, document)
