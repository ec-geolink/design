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


def main():
    ns = {
        "foaf": "http://xmlns.com/foaf/0.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "datacite": "http://purl.org/spar/datacite/",
        "owl": "http://www.w3.org/2002/07/owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "geosparql": "http://www.opengis.net/ont/geosparql#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "glview": "http://schema.geolink.org/dev/view#",
        "doview": "http://schema.geolink.org/dev/doview#",
        "prov": "http://www.w3.org/ns/prov#"
    }

    model = createModel()

    with open("people_dedupe.json", "rb") as infile:
        jsonfile = json.loads(infile.read())

    if len(jsonfile) <= 1:
        print "People file was read but didn't contain any content."
        sys.exit()

    """
    {
      "-- Hopkinsonchopkins@mbl.edu": [
        {
          "Id": "48852",
          "address": "The Ecosystems Center Marine Biological Laboratory Woods Hole MA 02543 United States of America",
          "document": "autogen.2012062607113784945.1",
          "email": "chopkins@mbl.edu",
          "format": "EML",
          "name": "-- Hopkinson",
          "organization": "",
          "phone": "508-289-7688",
          "type": "person"
        }
      ],
    """
    for record in jsonfile:
        identifier = str(uuid.uuid4())

        # Full name => glview:nameFull
        addStatement(model,
                     RDF.Uri(ns['glview']+identifier),
                     ns['glview'] + "nameFull",
                     record['full_name']
                     )
        # First name => glview:nameGiven
        addStatement(model,
                     RDF.Uri(ns['glview']+identifier),
                     ns['glview'] + "nameGiven",
                     record['full_name']
                     )
        # Last name => glview:nameFamily
        addStatement(model,
                     RDF.Uri(ns['glview']+identifier),
                     ns['glview'] + "nameFamily",
                     record['full_name']
                     )

    serialize(model, ns, "output.ttl", "turtle")


if __name__ == "__main__":
    main()
