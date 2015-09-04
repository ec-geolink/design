#!/usr/bin/python
# -*- coding: utf-8 -*-


""" create_graph.py

    Creates an RDF graph from a JSON dump.
"""

import sys
import json
import RDF
import uuid


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
    # Store people UUIDs
    people = []

    model = createModel()

    with open(filename, "rb") as infile:
        jsonfile = json.loads(infile.read())

    if len(jsonfile) <= 1:
        print "People file was read but didn't contain any content."
        sys.exit()

    """ Unroll `jsonfile`

        `jsonfile` contains a key 'unmatched' which is an array of the
        jsonfile not found to match any other record. We want to unroll this
        so all of the items in the array can be processed in the same sweep
        as the items that do have matches.

        We want to turn this:

        jsonfile = {
            'person1' : [person1a, person1b, ...],
            'person2' : [person2a, person2b, ...],
            'unmathced' : [person3, person 4, person 5, ...s]
        }

        Into this:

        jsonfile = [
            [person1a, person1b],
            [person2a, person2b],
            [person3],
            [person4],
            [person5]
        ]
    """

    unique_people = []

    if "unmatched" in jsonfile:
        for record in jsonfile['unmatched']:
            unique_people.append([record])

    for json_key in jsonfile:
        if json_key == "unmatched":
            continue

        unique_people.append(jsonfile[json_key])

    for unique_person in unique_people:
        # Make ID (temporary)
        identifier = str(uuid.uuid4())
        identifier_uri = RDF.Uri(ns['d1people']+identifier)
        people.append(identifier_uri)

        # Collect unique values of multiple values for each record
        salutations = []
        full_names = []
        first_names = []
        last_names = []
        organization_uris = []
        email_addresses = []
        mailing_addresses = []
        documents = []

        for record in unique_person:
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

            # Organization TODO Align this comment
            if len(record['organization']) > 0:
                if record['organization'] in organizations:
                    organization_uris.append(organizations[record['organization']])
                else:
                    print "Bad things happened for %s" % record['organization']
                    print record

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
    # Store UUID mappings
    organizations = {}

    model = createModel()

    with open(filename, "rb") as infile:
        jsonfile = json.loads(infile.read())

    if len(jsonfile) <= 1:
        print "People file was read but didn't contain any content."
        sys.exit()

    for key in jsonfile:
        # Make ID (temporary)
        identifier = str(uuid.uuid4())
        identifier_uri = RDF.Uri(ns['d1org']+identifier)
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

    organizations = createOrganizationGraph("organizations_unique.json", ns)
    createPeopleGraph("people_unique.json", ns, organizations)

if __name__ == "__main__":
    main()
