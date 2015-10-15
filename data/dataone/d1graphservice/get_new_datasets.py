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

from d1graphservice.people import processing

from d1graphservice import settings
from d1graphservice import dataone
from d1graphservice import util
from d1graphservice import validator
from d1graphservice import store
from d1graphservice import multi_store

from d1graphservice.people.formats import eml
from d1graphservice.people.formats import dryad
from d1graphservice.people.formats import fgdc


def extractCreators(identifier, document):
    """
    Detect the format of and extract people/organization creators from a document.

    Arguments:
        document:
            An XML document

    Returns:
        List of records.
    """

    # Detect the format
    metadata_format = processing.detectMetadataFormat(document)

    # Process the document for people/orgs
    if metadata_format == "eml":
        records = eml.process(document, identifier)
    elif metadata_format == "dryad":
        records = dryad.process(document, identifier)
    elif metadata_format == "fgdc":
        records = fgdc.process(document, identifier)
    else:
        print "Unknown format."
        records = []

    return records


def getSciMeta(identifier, identifier_map, cache_dir):
    """
    Retrieves scientific metadata from either a cache on the local filesystem
    or the CN.

    Returns:
        An XML document
    """

    scimeta = None

    if identifier in identifier_map:
        mapped_filename = identifier_map[identifier]
        mapped_file_path = cache_dir + mapped_filename

        if os.path.isfile(mapped_file_path):
            scimeta = ET.parse(mapped_file_path).getroot()
            print 'getting document from cache'

    if scimeta is None:
        print "getting doc off cn"
        scimeta = dataone.getDocument(identifier)

    return scimeta


def createIdentifierMap(path):
    """
    Converts a CSV of identifier<->filename mappings into a Dict.

    Returns:
        Dict of identifier<->filename mappings
    """

    identifier_map = None # Will be a docid <-> PID map

    if os.path.isfile(path):
        print "Loading identifiers map..."

        identifier_table = pandas.read_csv(path)
        identifier_map = dict(zip(identifier_table.guid, identifier_table.filepath))

    return identifier_map


def loadFormatsMap():
    """
    Gets the formats map from GitHub. These are the GeoLink URIs for the
    file format types DataOne knows about.

    Returns:
        A Dict of formats, indexed by format ID.
    """

    formats_table = pandas.read_csv("https://raw.githubusercontent.com/ec-geolink/design/master/data/dataone/formats/formats.csv")

    formats_map = {}

    for row_num in range(formats_table.shape[0]):
        fmt_id = formats_table['id'][row_num]
        fmt_name = formats_table['name'][row_num]
        fmt_type = formats_table['type'][row_num]
        fmt_uri = formats_table['uri'][row_num]

        formats_map[fmt_id] = { 'name': fmt_name, 'type': fmt_type, 'uri': fmt_uri }

    return formats_map


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

    # Load scimeta cache
    cache_dir = "/Users/mecum/src/d1dump/documents/"
    identifier_map = createIdentifierMap("/Users/mecum/src/d1dump/idents.csv")
    print "Read in %d identifier mappings." % len(identifier_map)

    # Load formats map
    print "Loading formats map from GitHub..."
    formats_map = loadFormatsMap()

    # Load triple stores
    namespaces = {
        "foaf": "http://xmlns.com/foaf/0.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "datacite": "http://purl.org/spar/datacite/",
        "owl": "http://www.w3.org/2002/07/owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "glview": "http://schema.geolink.org/dev/view/",
        "d1people": "https://dataone.org/person/",
        "d1org": "https://dataone.org/organization/",
        "d1resolve": "https://cn.dataone.org/cn/v1/resolve/",
        "prov": "http://www.w3.org/ns/prov#",
        "d1node": "https://cn.dataone.org/cn/v1/node/",
        "d1landing": "https://search.dataone.org/#view/",
        "d1repo": "https://cn.dataone.org/cn/v1/node/"
    }

    store_dict = {
        'people': store.Store("http://localhost:3030/", 'ds', namespaces),
        'organizations': store.Store("http://localhost:3131/", 'ds', namespaces),
        'datasets': store.Store("http://localhost:3232/", 'ds', namespaces)
    }



    stores = multi_store.MultiStore(store_dict, namespaces)

    # Create a record validator
    vld = validator.Validator()

    query_string = dataone.createSinceQuery(from_string, to_string, None, 0)
    num_results = dataone.getNumResults(query_string)

    # Calculate the number of pages we need to get to get all results
    page_size=1000
    num_pages = num_results / page_size
    if num_results % page_size > 0:
        num_pages += 1

    # Establish which fields we want to get from the Solr index
    fields = ["identifier","title","abstract","author",
    "authorLastName", "origin","submitter","rightsHolder","documents",
    "resourceMap","authoritativeMN","obsoletes","northBoundCoord",
    "eastBoundCoord","southBoundCoord","westBoundCoord","startDate","endDate",
    "datasource","replicaMN"]

    print "Found %d documents over %d page(s)." % (num_results, num_pages)

    # Process each page
    for page in range(1, num_pages + 1):
        print "Processing page %d." % page

        page_xml = dataone.getSincePage(from_string, to_string, fields, page, page_size)
        docs = page_xml.findall(".//doc")

        for doc in docs:
            identifier = doc.find("./str[@name='identifier']").text
            print "Adding dataset for %s. " % identifier

            scimeta = getSciMeta(identifier, identifier_map, cache_dir)

            if scimeta is None:
                print "Unable to get scimeta for %s. Skipping." % identifier

            records = extractCreators(identifier, scimeta)

            print "Found %d record(s)." % len(records)

            # Add records and organizations
            people = [p for p in records if 'type' in p and p['type'] == 'person']
            organizations = [o for o in records if 'type' in o and o['type'] == 'organization']

            # Always do organizations first, so peoples' organization URIs exist
            for organization in organizations:
                organization = vld.validate(organization)
                stores.addOrganization(organization)

            for person in people:
                person = vld.validate(person)
                stores.addPerson(person)

            stores.addDataset(doc, scimeta, formats_map)


    stores.save()

    # Save settings
    # config['last_run'] = to_string
    # util.saveJSONFile(config, 'settings.json')

    return


if __name__ == "__main__":
    main()
