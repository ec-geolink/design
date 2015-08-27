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
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

from people.formats import eml
from people.formats import dryad
from people.formats import fgdc


def processDirectory(job):
    filenames = os.listdir("%s" % job.directory)

    i = 0
    for filename in filenames:
        print i
        try:
            xmldoc = ET.parse("%s/%s" % (job.directory, filename))
        except ParseError:
            continue

        processDocument(job, xmldoc, filename)
        i += 1


def processDocument(job, xmldoc, filename):
    """ Process an individual document."""
    document = filename

    root = xmldoc.getroot()

    if re.search("eml$", root.tag):
        records = eml.process(job, xmldoc, document)

        if records is not None:
            saveRecords(job, records)

    elif re.search("Dryad", root.tag):
        records = dryad.process(job, xmldoc, document)

        if records is not None:
            saveRecords(job, records)

    elif re.search("metadata", root.tag):
        records = fgdc.process(job, xmldoc, document)

        if records is not None:
            saveRecords(job, records)

    else:
        print "Unknown format: %s" % root.tag


def saveRecords(job, records):
    """Saves an array of records to disk, according to their filename"""

    if records is None:
        return

    for record in records:
        if record['type'] == 'person':
            job.writePerson(record)
        elif record['type'] == 'organization':
            job.writeOrganization(record)
