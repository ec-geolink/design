"""
    filename:   create-d1-formats-graph.py
    author:     Bryce Mecum (mecum@nceas.ucsb.edu)

    Creates an RDF graph of D1 formats for use in other graphs.
"""


def createModel():
    """Creates an RDF Model to add triples to."""

    storage=RDF.Storage(storage_name="hashes", name="geolink", options_string="new='yes',hash-type='memory',dir='.'")

    if storage is None:
        raise Exception("new RDF.Storage failed")

    model=RDF.Model(storage)

    if model is None:
        raise Exception("new RDF.Model failed")

    return model

def serializeModel(model, ns, filename, format):
    """Serializes the RDF Model to disk in the specified format."""

    if format==None:
        format="turtle"

    serializer=RDF.Serializer(name=format)

    for prefix in ns:
        serializer.set_namespace(prefix, RDF.Uri(ns[prefix]))

    serializer.serialize_model_to_file(filename, model)


def addStatement(model, s, p, o):
    """Utility function to make adding RDF statements to the Model easier."""

    # Assume subject is a URI string if it is not an RDF.Node
    if (type(s) is not RDF.Node):
        s_node = RDF.Uri(s)
    else:
        s_node = s

    # Assume predicate is a URI string if it is not an RDF.Node
    if (type(p) is not RDF.Node):
        p_node = RDF.Uri(p)
    else:
        p_node = p

    # Assume object is a literal if it is not an RDF.Node
    if (type(o) is not RDF.Node):
        o_node = RDF.Node(o)
    else:
        o_node = o
    statement=RDF.Statement(s_node, p_node, o_node)

    if statement is None:
        raise Exception("new RDF.Statement failed")

    model.add_statement(statement)


def main():
    """The program essentially runs three operations

        First, the RDF Model and namespaces are created. Then the script fetches
        the formats list off of DataOne. Then, for each format found,
        a corresponding set of statements are made in the RDF graph about that
        format. Finally, the RDF graph is serialized to disk on both RDF/XML
        and Turtle formats.
    """

    # Setup
    model = createModel()
    ns = {
        "owl": "http://www.w3.org/2002/07/owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "datacite": "http://purl.org/spar/datacite/",
        "glview": "http://schema.geolink.org/dev/view#",
        "doview": "http://schema.geolink.org/dev/doview#",
        "ecglvoc_format" : "http://schema.geolink.org/dev/voc/dataone/format#"
    }


    # Get formats list
    try:
        req = urllib2.urlopen("https://cn.dataone.org/cn/v1/formats")
    except:
        print "Failed to open formats URL. Exiting."

        return

    content = req.read()
    xmldoc = ET.fromstring(content)
    format_nodes = xmldoc.findall(".//objectFormat")

    format_index = 1 # Used to give formats URIs

    for fmt in format_nodes:
        format_id = fmt.find("./formatId").text
        format_name = fmt.find("./formatName").text
        format_type = fmt.find("./formatType").text

        # Create this format's URI and URI node
        format_uri = ns["ecglvoc_format"] + str(format_index).rjust(3, "0")
        format_uri_node = RDF.Uri(format_uri)

        # Name and Type
        addStatement(model, format_uri, RDF.Uri(ns["rdf"] + "type"), RDF.Uri(ns["glview"] + "Format"))
        addStatement(model, format_uri, RDF.Uri(ns["glview"] + "description"), format_name)
        addStatement(model, format_uri, RDF.Uri(ns["glview"] + "formatType"), format_type)

        # Identifier
        id_blank_node = RDF.Node(blank=format_uri)

        addStatement(model, id_blank_node, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["datacite"]+"ResourceIdentifier"))
        addStatement(model, id_blank_node, ns["glview"]+"hasIdentifierValue", format_id)
        addStatement(model, id_blank_node, ns["rdfs"]+"label", format_id)
        addStatement(model, id_blank_node, ns["glview"]+"hasIdentifierScheme", RDF.Uri(ns["datacite"] + "local-resource-identifier-scheme"))

        addStatement(model, format_uri, RDF.Uri(ns["glview"] + "identifier"), id_blank_node)


        format_index += 1

    # Serialize graph to disk
    serializeModel(model, ns, "formats.ttl", "turtle")
    serializeModel(model, ns, "formats.xml", "rdfxml")



if __name__ == "__main__":
    import RDF
    import urllib2
    import xml.etree.ElementTree as ET
    import string
    import sys
    import os

    main()
