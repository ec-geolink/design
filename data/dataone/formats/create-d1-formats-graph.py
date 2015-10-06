"""
    filename:   create-d1-formats-graph.py
    author:     Bryce Mecum (mecum@nceas.ucsb.edu)

    Creates an RDF graph of D1 formats for use in other graphs.

    Because this process results in minting LOD URIs for formats and we never
    want to change or delete the mapping between a LOD URI and what it points
    to, this script keeps track of what URIs<->Format mappings its made and
    correctly mints new URIs for new formats.

    New formats enter the graph when DataOne adds a format at:

        https://cn.dataone.org/cn/v1/formats

    All URIs are on the base:

        http://schema.geolink.org/dev/voc/dataone/format#
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


def getFormats():
    """Gets the formats list from the DataOne CN.

    Returns a Dict index by format id
        Each element containing the ID, type, and name of the format.
    """

    try:
        req = urllib2.urlopen("https://cn.dataone.org/cn/v1/formats")
    except:
        print "Failed to open formats URL. Exiting."
        return

    content = req.read()
    xmldoc = ET.fromstring(content)
    format_nodes = xmldoc.findall(".//objectFormat")

    formats = {}

    for format_node in format_nodes:
        format_id = format_node.find("./formatId").text
        format_name = format_node.find("./formatName").text
        format_type = format_node.find("./formatType").text

        formats[format_id] = { 'id': format_id,
                                'name': format_name,
                                'type': format_type }

    return formats


def createGraph(model, formats, ns):
    """Adds formats to the RDF model"""

    for fmt in formats:
        # Create this format's URI node
        format_uri_node = RDF.Uri(formats[fmt]['uri'])

        # Name and Type
        addStatement(model, formats[fmt]['uri'], RDF.Uri(ns["rdf"] + "type"), RDF.Uri(ns["ecglvoc_format"] + "Format"))
        addStatement(model, formats[fmt]['uri'], RDF.Uri(ns["glbase"] + "description"), formats[fmt]['name'])
        addStatement(model, formats[fmt]['uri'], RDF.Uri(ns["glbase"] + "formatType"), formats[fmt]['type'])

        # Identifier node
        id_blank_node = RDF.Node(blank=formats[fmt]['uri'])

        addStatement(model, id_blank_node, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["glbase"]+"Identifier"))
        addStatement(model, id_blank_node, ns["glbase"]+"hasIdentifierValue", fmt)
        addStatement(model, id_blank_node, ns["glbase"]+"hasIdentifierScheme", RDF.Uri(ns["datacite"] + "local-resource-identifier-scheme"))
        addStatement(model, id_blank_node, ns["rdfs"]+"label", fmt)

        addStatement(model, formats[fmt]['uri'], RDF.Uri(ns["glbase"] + "hasIdentifier"), id_blank_node)


def main():
    """This method updates the DataOne formats in a few steps:

        1. Load existing formats from disk
        2. Check the official formats list on DataOne
        3. Mint new URIs for formats on DataOne that are not already on disk
        4. Serialize a TTL and RDF/XML graph to disk
        5. Save the updated list of formats
    """


    # Setup
    model = createModel()

    ns = {
        "owl": "http://www.w3.org/2002/07/owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "datacite": "http://purl.org/spar/datacite/",
        "glbase": "http://schema.geolink.org/dev/base/main#",
        "ecglvoc_format" : "http://schema.geolink.org/dev/voc/dataone/format#"
    }


    # Load in existing formats
    formats = {}

    if os.path.isfile("formats.csv"):
        print "Loading existing formats from disk..."

        with open("formats.csv", "rU") as f:
            reader = csv.DictReader(f)

            for row in reader:
                formats[row['id']] = { 'idx': row['idx'],
                                              'id': row['id'],
                                              'type':row['type'],
                                              'name': row['name'],
                                              'uri': row['uri'] }

        print "  Loaded %d formats from disk." % len(formats)


    # Get DataOne formats
    print "Querying DataOne for the formats list..."

    format_list = getFormats()

    print "  Found %d formats on DataOne." % len(format_list)


    # Find the formats not on disk
    new_formats = {}

    for fmt in format_list:
        if fmt not in formats:
            new_formats[fmt] = format_list[fmt]

    print "Found %d new format(s)." % len(new_formats)


    # Find the highest idx
    highest_idx = 0

    for fmt in formats:
        if int(formats[fmt]['idx']) > highest_idx:
            highest_idx = int(formats[fmt]['idx'])

    for fmt in new_formats:
        highest_idx += 1
        # Mint the new URI
        formats[fmt] = { 'idx': highest_idx,
                                'id': fmt,
                                'type': new_formats[fmt]['type'],
                                'name': new_formats[fmt]['name'],
                                'uri': ns['ecglvoc_format'] + str(highest_idx).rjust(3, "0") }
        print "Added format %s." % formats[fmt]['uri']

    createGraph(model, formats, ns)


    # Serialize graph to disk
    serializeModel(model, ns, "formats.ttl", "turtle")
    serializeModel(model, ns, "formats.xml", "rdfxml")


    # Write the CSV to file
    if formats:
        with open("formats.csv", "w") as f:
            field_names = ['idx', 'id', 'type', 'name', 'uri']
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()

            sorted_formats = sorted(formats, key=lambda k: int(formats[k]['idx']))

            for fmt in sorted_formats:
                writer.writerow(formats[fmt])



if __name__ == "__main__":
    import os
    import RDF
    import urllib2
    import xml.etree.ElementTree as ET
    import csv

    main()
