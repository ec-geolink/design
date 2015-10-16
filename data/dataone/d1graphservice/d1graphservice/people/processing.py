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

from d1graphservice.people.formats import eml
from d1graphservice.people.formats import dryad
from d1graphservice.people.formats import fgdc


def processDirectory(job):
    filenames = os.listdir("%s" % job.directory)

    i = 0
    for filename in filenames:
        if i % 1000 == 0:
            print "%d..." % i

        try:
            xmldoc = ET.parse("%s/%s" % (job.directory, filename))
        except ParseError:
            continue

        processDocument(job, xmldoc, filename)
        i += 1

    print "Processed a total of %d documents" % i


def detectMetadataFormat(xmldoc):
    """ Detect the format of the metadata in `xmldoc`.

    """

    root = xmldoc

    if re.search("eml$", root.tag):
        return "eml"
    elif re.search("Dryad", root.tag):
        return "dryad"
    elif re.search("metadata", root.tag):
        return "fgdc"
    else:
        return "unknown"


def extractCreators(identifier, doc):
    """
    Detect the format of and extract people/organization creators from a document.

    Arguments:
        document: str
            The document's PID

        doc:
            An XML document of the scientific metadata

    Returns:
        List of records.
    """

    if doc is None:
        raise Exception("No XML document was passed.")

    # Detect the format
    metadata_format = detectMetadataFormat(doc)

    # Process the document for people/orgs
    if metadata_format == "eml":
        records = eml.process(doc, identifier)
    elif metadata_format == "dryad":
        records = dryad.process(doc, identifier)
    elif metadata_format == "fgdc":
        records = fgdc.process(doc, identifier)
    else:
        print "Unknown format."
        records = []

    return records


def processDocument(job, xmldoc, filename):
    """ Process an individual document."""
    document = filename

    # Strip trailing revision number from filename
    just_pid = re.match("(autogen.\d+)\.\d", document)

    if just_pid is not None:
        document = just_pid.groups(0)[0]

    # Map the filename to its PID if we have a map to go off of
    if job.identifier_map is not None:
        if document in job.identifier_map:
            document = job.identifier_map[document]

    # Null out the document PID if it's not public
    if job.public_pids is not None:
        if document not in job.public_pids:
            document = ''

    records = extractCreators(document, xmldoc)

    if records is not None:
        saveRecords(job, records)


def saveRecords(job, records):
    """Saves an array of records to disk, according to their filename"""

    if records is None:
        return

    for record in records:
        # Skip empty records
        if 'type' not in record:
            continue

        if record['type'] == 'person':
            job.writePerson(record)

            # Add their organization too (if applicable)
            if 'organization' in record and len(record['organization']) > 0:
                org_record = {
                    'name': record['organization'],
                    'format': record['format'],
                    'source': record['source'],
                    'document': record['document']
                }

                job.writeOrganization(org_record)

        elif record['type'] == 'organization':
            job.writeOrganization(record)
