#!/usr/bin/python
# -*- coding: utf-8 -*-


""" create_graph.py

    Creates an RDF graph from a JSON dump.
"""

import os
import sys
import json
import RDF
import uuid
import pandas
import unicodecsv as csv


def addStatement(model, s, p, o):
    # Assume subject is a URI string if it is not an RDF.Node
    if type(s) is not RDF.Node:
        s_node = RDF.Uri(s)
    else:
        s_node = s

    # Assume predicate is a URI string if it is not an RDF.Node
    if type(p) is not RDF.Node:
        p_node = RDF.Uri(p)
    else:
        p_node = p

    # Assume object is a literal if it is not an RDF.Node
    if type(o) is not RDF.Node:
        o_node = RDF.Node(o)
    else:
        o_node = o

    statement = RDF.Statement(s_node, p_node, o_node)

    if statement is None:
        raise Exception("new RDF.Statement failed")

    model.add_statement(statement)


def createModel():
    storage = RDF.Storage(storage_name="hashes",
                          name="geolink",
                          options_string="new='yes',hash-type='memory',dir='.'"
                          )

    if storage is None:
        raise Exception("new RDF.Storage failed")

    model = RDF.Model(storage)

    if model is None:
        raise Exception("new RDF.model failed")

    return model


def serialize(model, ns, filename, format):
    if format is None:
        format = "turtle"

    serializer = RDF.Serializer(name=format)

    for prefix in ns:
        serializer.set_namespace(prefix, RDF.Uri(ns[prefix]))

    serializer.serialize_model_to_file(filename, model)


def createPeopleGraph(filename, ns={}, organizations={}):
    # Store/retrieve people URIs
    if os.path.isfile("people_uris.csv"):
        print "Loading existing people URI mapping file."

        people = pandas.Series.from_csv("people_uris.csv", encoding='utf-8').to_dict()

        print len(people)
    else:
        print "Creating people mappings from scratch."
        people = {}

    # Create RDF Model
    model = createModel()

    # Load people file
    with open(filename, "rb") as infile:
        jsonfile = json.loads(infile.read())

    # Check the file for content
    if len(jsonfile) < 1:
        print "People file was read but didn't contain any content."
        sys.exit()

    # Unroll the unmatched records before processing
    if 'unmatched' in jsonfile:
        print "Unrolling unmatchable records before processing..."

        unmatched_count = len(jsonfile['unmatched'])

        for i in range(0, unmatched_count):
            jsonfile['unmatched' + str(i)] =  [jsonfile['unmatched'][i]]

        del jsonfile['unmatched']

    # Process each key
    for key in jsonfile:
        records = jsonfile[key] # Array of people instances

        existing_uri = findPeopleUri(people, key)

        if existing_uri is None:
            existing_uri = mintPeopleUri(people, key, ns)
            people[key] = existing_uri

        identifier_uri = existing_uri

        # Collect unique values of multiple values for each record
        salutations = []
        full_names = []
        first_names = []
        last_names = []
        organization_uris = []
        email_addresses = []
        mailing_addresses = []
        documents = []

        for record in records:
            # Full name => glview:namePrefix
            if len(record['salutation']) > 0:
                salutations.append(record['salutation'])

            # Full name => glview:nameFull
            if len(record['full_name']) > 0:
                full_names.append(record['full_name'])

            # First name => glview:nameGiven
            if len(record['first_name']) > 0:
                first_names.append(record['first_name'])

            # Last name => glview:nameFamily
            if len(record['last_name']) > 0:
                last_names.append(record['last_name'])

            # Organization
            if len(record['organization']) > 0:
                existing_uri = findOrganizationUri(organizations, record['organization'])

                if existing_uri is None:
                    existing_uri = mintOrganizationUri(organizations, record['organization'], ns)
                    organizations[record['organization']] = existing_uri

                organization_uris.append(existing_uri)

            # Email address => foaf:mbox
            if len(record['email']) > 0:
                email_addresses.append(record['email'])

            # Mailing address => TODO
            if len(record['address']) > 0:
                mailing_addresses.append(record['address'])

            # Documents => glview:Dataset
            if len(record['document']) > 0:
                documents.append(record['document'])

        # Add statements to RDF Graph

        # Full name => glview:namePrefix
        for salutation in salutations:
            addStatement(model,
                         identifier_uri,
                         ns['glview'] + "namePrefix",
                         salutation
                         )

        # Full name => glview:nameFull
        for full_name in full_names:
            addStatement(model,
                         identifier_uri,
                         ns['glview'] + "nameFull",
                         full_name
                         )

        # First name => glview:nameGiven
        for given_name in first_names:
            addStatement(model,
                         identifier_uri,
                         ns['glview'] + "nameGiven",
                         given_name
                         )

        # Last name => glview:nameFamily
        for last_name in last_names:
            addStatement(model,
                         identifier_uri,
                         ns['glview'] + "nameFamily",
                         last_name
                         )
        # Organizations
        for organization_uri in organization_uris:
            addStatement(model,
                         identifier_uri,
                         ns['glview'] + "hasAffilitation",
                         RDF.Uri(organization_uri))
        # Email
        for email in email_addresses:
            addStatement(model,
                         identifier_uri,
                         ns['foaf'] + "mbox",
                         RDF.Uri("mailto:" + email))

        # Address
        for address in mailing_addresses:
            addStatement(model,
                         identifier_uri,
                         ns['glview'] + "address",
                         address)

        # Documents
        for document in documents:
            addStatement(model,
                         identifier_uri,
                         ns['glview'] + "isCreatorOf",
                         RDF.Uri(ns['d1resolve'] + document))

    serialize(model, ns, "../../people.ttl", "turtle")

    return people


def createOrganizationGraph(filename, ns={}):
    # Store/retrieve organization URIs
    if os.path.isfile("organization_uris.csv"):
        print "Loading existing organization URI mapping file."
        organizations = pandas.Series.from_csv("organization_uris.csv", encoding='utf-8').to_dict()
        print len(organizations)
    else:
        print "Creating organization mappings from scratch."
        organizations = {}

    model = createModel()

    with open(filename, "rb") as infile:
        jsonfile = json.loads(infile.read())

    if len(jsonfile) < 1:
        print "Organization file was read but didn't contain any content."
        sys.exit()

    for key in jsonfile:
        identifier_uri = findOrganizationUri(organizations, key)

        if identifier_uri is None:
            identifier_uri = mintOrganizationUri(organizations, key, ns)
            organizations[key] = identifier_uri

        # Collect unique values of multiple values for each record
        names = []
        email_addresses = []
        mailing_addresses = []
        documents = []

        # Iterate through each record of each unique person
        records = jsonfile[key]

        for record in records:
            # Full name => glview:namePrefix
            if len(record['name']) > 0:
                names.append(record['name'])

        # Email address => foaf:mbox
        if len(record['email']) > 0:
            email_addresses.append(record['email'])

        # Mailing address => TODO
        if len(record['address']) > 0:
            mailing_addresses.append(record['address'])

        # Documents => glview:Dataset
        if len(record['document']) > 0:
            documents.append(record['document'])

        # Add statements to RDF Graph

        # Full name => glview:namePrefix
        for name in names:
            addStatement(model,
                         identifier_uri,
                         ns['rdf'] + "label",
                         name
                         )

        # Email
        for email in email_addresses:
            addStatement(model,
                         identifier_uri,
                         ns['foaf'] + "mbox",
                         RDF.Uri("mailto:" + email))

        # Address
        for address in mailing_addresses:
            addStatement(model,
                         identifier_uri,
                         ns['glview'] + "address",
                         address)

        # Documents
        for document in documents:
            addStatement(model,
                         identifier_uri,
                         ns['glview'] + "isCreatorOf",
                         RDF.Uri(ns['d1resolve'] + document))

    serialize(model, ns, "../../organizations.ttl", "turtle")

    return organizations

def findPeopleUri(people, key):
    """ Given a pandas.DataFrame of people, look for key and return either
    the existing URI for that key, or mint a new URI and return that.
    """

    identifier_uri_string = None

    if key in people:
        identifier_uri_string = people[key]

    return identifier_uri_string


def findOrganizationUri(organizations, key):
    """ Given a pandas.DataFrame of organizations, look for key and return
        either the existing URI for that key, or mint a new URI and return that.
    """

    identifier_uri_string = None

    if key in organizations:
        identifier_uri_string = organizations[key]

    return identifier_uri_string


def mintPeopleUri(people, key, ns):
    """ Mints and returns the people URI string for key `key`"""

    # Make UUID and URI string
    identifier = str(uuid.uuid4())
    identifier_uri_string = ''.join([ns['d1people'], 'urn:uuid:', identifier])

    print "Minting new person URI for %s <=> %s." % (key.encode('utf-8'), identifier_uri_string.encode('utf-8'))

    return identifier_uri_string


def mintOrganizationUri(organizations, key, ns):
    """ Mints and returns the organization URI string for key `key`"""

    # Make UUID and URI string
    identifier = str(uuid.uuid4())
    identifier_uri_string = ''.join([ns['d1org'], 'urn:uuid:', identifier])

    print "Minting new organization URI for %s <=> %s." % (key.encode('utf-8'), identifier_uri_string.encode('utf-8'))

    return identifier_uri_string


def main():
    ns = {
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
        "d1resolve": "https://cn.dataone.org/cn/v1/resolve/"
    }

    """ Create organization graph first, then do people
        We do this because people re-use the URIs minted/re-used for
        organizations
    """

    print "Creating organization graph..."
    organizations = createOrganizationGraph("organizations_unique.json", ns)

    print "Creating people graph..."
    people = createPeopleGraph("people_unique.json", ns, organizations)

    with open("organization_uris.csv", "wb") as outfile:
        w = csv.writer(outfile, encoding='utf-8')
        w.writerow(('key', 'uri'))

        for key in organizations:
            w.writerow((key, organizations[key]))


    with open("people_uris.csv", "wb") as outfile:
        w = csv.writer(outfile, encoding='utf-8')
        w.writerow(('key', 'uri'))

        for key in people:
            w.writerow((key, people[key]))



if __name__ == "__main__":
    main()
