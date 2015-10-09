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
import pandas
import xml.etree.ElementTree as ET

from people import processing
from people.formats import eml
from people.formats import dryad
from people.formats import fgdc

from service import settings
from service import dataone
from service import util
from service import dedupe
from service import store
from service import validator


def main():
    # Settings
    config = util.loadJSONFile('settings.json')

    if 'last_run' not in config:
        print "Last run datetime not found in settings.json. Exiting."
        sys.exit()

    # Create from and to strings
    # from_string = config['last_run']
    # to_string = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S.0Z")

    from_string = "2015-01-06T16:00:00.0Z"
    to_string = "2015-01-06T16:05:00.0Z"

    # Get document identifiers
    identifiers = dataone.getDocumentIdentifiersSince(from_string, to_string)
    print "Retrieved %d identifiers." % len(identifiers)

    # Load scimeta cache
    cache_dir = "/Users/mecum/src/d1dump/documents/"
    identifier_map_filepath = "/Users/mecum/src/d1dump/idents.csv"
    identifier_map = None # Will be a docid <-> PID map

    if os.path.isfile(identifier_map_filepath):
        print "Loading identifiers map..."

        identifier_table = pandas.read_csv(identifier_map_filepath)
        identifier_map = dict(zip(identifier_table.guid, identifier_table.filepath))

        print "Read in %d identifier mappings." % len(identifier_map)
        print identifier_table.head()

    # Load triple stores
    d1people = store.Store("http://localhost:3030/", 'ds')
    d1orgs = store.Store("http://localhost:3131/", 'ds')
    d1datasets = store.Store("http://localhost:3232/", 'ds')

    print "d1people store initial size %s" % d1people.count()
    print "d1orgs store initial size %s" % d1orgs.count()
    print "d1datasets store initial size %s" % d1datasets.count()

    # Create a record validator
    vld = validator.Validator()

    # Get documents themselves
    for identifier in identifiers:
        print "----------"
        print "Getting document with identifier `%s`" % identifier

        # Decide to grab from CN or from cache
        doc = None
    query_string = dataone.createSinceQuery(from_string, to_string, None, 0)
    num_results = dataone.getNumResults(query_string)

    # Calculate the number of pages we need to get to get all results
    page_size=1000
    num_pages = num_results / page_size
    if num_results % page_size > 0:
        num_pages += 1

    fields = ["identifier","title","abstract","author",
    "authorLastName", "origin","submitter","rightsHolder","documents",
    "resourceMap","authoritativeMN","obsoletes","northBoundCoord",
    "eastBoundCoord","southBoundCoord","westBoundCoord","startDate","endDate",
    "datasource","replicaMN"]

    print "Found %d documents over %d page(s)." % (num_results, num_pages)

        if identifier in identifier_map:
            mapped_filename = identifier_map[identifier]
            mapped_file_path = cache_dir + mapped_filename
    for page in range(1, num_pages + 1):
        doc = dataone.getSincePage(from_string, to_string, fields, page, page_size)

            if os.path.isfile(mapped_file_path):
                doc = ET.parse(mapped_file_path).getroot()
        docs = doc.findall(".//doc")

        if doc is None:
            doc = dataone.getDocument(identifier)
        for doc in docs:
            identifier = doc.find("./str[@name='identifier']").text
            print "Adding dataset for %s. " % identifier

        # Detect the format
        fmt = processing.detectMetadataFormat(doc)
            scimeta = None

        # Process the document for people/orgs
        if fmt == "eml":
            records = eml.process(doc, identifier)
        elif fmt == "dryad":
            records = dryad.process(doc, identifier)
        elif fmt == "fgdc":
            records = fgdc.process(doc, identifier)
        else:
            print "Unknown format."
            if identifier in identifier_map:
                mapped_filename = identifier_map[identifier]
                mapped_file_path = cache_dir + mapped_filename

        print "Found %d record(s)." % len(records)
                if os.path.isfile(mapped_file_path):
                    scimeta = ET.parse(mapped_file_path).getroot()
                    print 'getting document from cache'

        # Add records and organizations
        people = [p for p in records if 'type' in p and p['type'] == 'person']
        organizations = [o for o in records if 'type' in o and o['type'] == 'organization']
            if scimeta is None:
                print "getting doc off cn"
                scimeta = dataone.getDocument(identifier)

        for organization in organizations:
            organization = vld.validate(organization)
            # Detect the format
            fmt = processing.detectMetadataFormat(scimeta)

            if organization is None:
                continue
            # Process the document for people/orgs
            if fmt == "eml":
                records = eml.process(scimeta, identifier)
            elif fmt == "dryad":
                records = dryad.process(scimeta, identifier)
            elif fmt == "fgdc":
                records = fgdc.process(scimeta, identifier)
            else:
                print "Unknown format."
                records = []

            d1orgs.addOrganization(organization)
            print "Found %d record(s)." % len(records)

        for person in people:
            person = vld.validate(person)
            # Add records and organizations
            people = [p for p in records if 'type' in p and p['type'] == 'person']
            organizations = [o for o in records if 'type' in o and o['type'] == 'organization']

            if person is None:
                continue
            # Always do organizations first, so peoples' organization URIs exist
            for organization in organizations:
                organization = vld.validate(organization)
                d1orgs.addOrganization(organization)

            d1people.addPerson(person)
            for person in people:
                person = vld.validate(person)
                d1people.addPerson(person)

        # store.addDataset(identifier)
            d1datasets.addDataset(doc)


    d1people.export("d1people.ttl")
    d1orgs.export("d1orgs.ttl")
    d1datasets.export("d1datasets.ttl")

    # Save settings
    # config['last_run'] = to_string
    # util.saveJSONFile(config, 'settings.json')

    return


if __name__ == "__main__":
    main()
