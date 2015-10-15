"""
Process a dataset (by PID) for dataset/people/org triples.
"""

import os
import sys
import datetime
import json
import uuid
import pandas
import xml.etree.ElementTree as ET
import urllib

from d1graphservice.people import processing

from d1graphservice import settings
from d1graphservice import dataone
from d1graphservice import util
from d1graphservice import validator
from d1graphservice import store
from d1graphservice import multi_store

from d1graphservice.people import processing

from d1graphservice.people.formats import eml
from d1graphservice.people.formats import dryad
from d1graphservice.people.formats import fgdc


if __name__ == "__main__":
    cache_dir = "/Users/mecum/src/d1dump/documents/"
    formats_map = util.loadFormatsMap()

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

    # Load triple stores
    stores = {
        'people': store.Store("http://localhost:3030/", 'ds', namespaces),
        'organizations': store.Store("http://localhost:3131/", 'ds', namespaces),
        'datasets': store.Store("http://localhost:3232/", 'ds', namespaces)
    }

    stores = multi_store.MultiStore(stores, namespaces)

    identifier = 'doi:10.5063/AA/nceas.920.2'

    # Establish which fields we want to get from the Solr index
    fields = ["identifier","title","abstract","author",
    "authorLastName", "origin","submitter","rightsHolder","documents",
    "resourceMap","authoritativeMN","obsoletes","northBoundCoord",
    "eastBoundCoord","southBoundCoord","westBoundCoord","startDate","endDate",
    "datasource","replicaMN"]


    identifier_esc = urllib.quote_plus(identifier)
    vld = validator.Validator()

    scimeta = dataone.getScientificMetadata(identifier)
    doc = dataone.getSolrIndex(identifier, fields)
    records = processing.extractCreators(identifier, scimeta)

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
