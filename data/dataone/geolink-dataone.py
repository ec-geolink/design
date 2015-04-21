#!/opt/local/bin/python
#
# A quick demo script showing generation of GeoLink-ish RDF from DataONE data sets for a Linked Open Data demo
# See http://schema.geolink.org for schema and namespace details
# See http://releases.dataone.org/online/api-documentation-v1.2.0/ for details of the DataONE API
#
# Matt Jones, NCEAS 2015

def getDataList():
    d1query = "https://cn.dataone.org/cn/v1/query/solr/?fl=identifier,title,author,authorLastName,origin,submitter,rightsHolder,relatedOrganizations,contactOrganization,documents,resourceMap&q=formatType:METADATA+AND+(datasource:*LTER+OR+datasource:*KNB+OR+datasource:*PISCO)+AND+-obsoletedBy:*&rows=100&start=0"
    #d1query = "https://cn.dataone.org/cn/v1/query/solr/?fl=identifier,title,author,authorLastName,origin,submitter,rightsHolder,relatedOrganizations,contactOrganization,documents,resourceMap&q=formatType:METADATA&rows=100&start=20000"
    res = urllib2.urlopen(d1query)
    content = res.read()
    xmldoc = ET.fromstring(content)
    return(xmldoc)

def addStatement(model, s, p, o):
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
    print(statement)
    model.add_statement(statement)

def addDataset(model, doc, ns, personhash):
    d1base = "https://cn.dataone.org/cn/v1/resolve/"

    # Identifier and Dataset
    element = doc.find("./str[@name='identifier']")
    identifier = element.text
    addStatement(model, d1base+identifier, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", RDF.Uri(ns["glview"]+"Dataset"))
    id_blank_node = RDF.Node(blank=identifier)
    addStatement(model, id_blank_node, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", RDF.Uri(ns["datacite"]+"ResourceIdentifier"))
    addStatement(model, d1base+identifier, ns["glview"]+"identifier", id_blank_node)
    addStatement(model, id_blank_node, ns["glview"]+"hasIdentifierValue", identifier)
    if (identifier.startswith("doi:") | 
            identifier.startswith("http://doi.org/") | identifier.startswith("https://doi.org/") | 
            identifier.startswith("https://dx.doi.org/") | identifier.startswith("https://dx.doi.org/")):
        scheme = 'doi'
    elif (identifier.startswith("ark:")):
        scheme = 'ark'
    elif (identifier.startswith("http:")):
        scheme = 'uri'
    elif (identifier.startswith("https:")):
        scheme = 'uri'
    elif (identifier.startswith("urn:")):
        scheme = 'urn'
    else:
        scheme = 'local-resource-identifier-scheme'
    addStatement(model, id_blank_node, ns["glview"]+"hasIdentifierScheme", RDF.Uri(ns["datacite"]+scheme))

    # Title
    title_element = doc.find("./str[@name='title']")
    addStatement(model, d1base+identifier, ns["glview"]+"title", title_element.text)
    
    # Creators
    originlist = doc.findall("./arr[@name='origin']/str")
    for creatornode in originlist:
        creator = creatornode.text
        if (creator not in personhash):
            # Add it
            newid = uuid.uuid4()
            p_uuid = newid.urn
            p_orcid = "http://myfakeorcid.org/" + newid.hex
            p_data = [p_uuid, p_orcid]
            personhash[creator] = p_data
        else:
            # Look it up
            p_data = personhash[creator]
            p_uuid = p_data[0]
            p_orcid = p_data[1]
            
        # Person
        addStatement(model, p_uuid, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", RDF.Uri(ns["glview"]+"Person"))
        addStatement(model, p_uuid, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", RDF.Uri(ns["foaf"]+"Person"))
        addStatement(model, p_uuid, ns["foaf"]+"name", creator)
        addStatement(model, RDF.Uri(d1base+identifier), RDF.Uri(ns["dcterms"]+"creator"), RDF.Uri(p_uuid))
        
        # ORCID
        pi_node = RDF.Node(RDF.Uri(p_orcid))
        addStatement(model, pi_node, RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), RDF.Uri(ns["datacite"]+"PersonalIdentifier"))       
        addStatement(model, pi_node, RDF.Uri(ns["datacite"]+"usesIdentifierScheme"), RDF.Uri(ns["datacite"]+"orcid"))       
        addStatement(model, RDF.Uri(p_uuid), RDF.Uri(ns["datacite"]+"hasIdentifier"), pi_node)
        model.sync()


    # Submitters
    # Rights holders
    # Repository
    # Landing page
    # Funding
    # MeasurementType

    # Data Objects

def createModel():
    storage=RDF.Storage(storage_name="hashes", name="geolink", options_string="new='yes',hash-type='memory',dir='.'")
    #storage=RDF.MemoryStorage()
    if storage is None:
        raise Exception("new RDF.Storage failed")
    model=RDF.Model(storage)
    if model is None:
        raise Exception("new RDF.model failed")
    return model

def serialize(model, ns, filename, format):
    # Format can be one of:
    # rdfxml          RDF/XML (default)
    # ntriples        N-Triples
    # turtle          Turtle Terse RDF Triple Language
    # trig            TriG - Turtle with Named Graphs
    # rss-tag-soup    RSS Tag Soup
    # grddl           Gleaning Resource Descriptions from Dialects of Languages
    # guess           Pick the parser to use using content type and URI
    # rdfa            RDF/A via librdfa
    # nquads          N-Quads
    if format==None:
        format="turtle"
    serializer=RDF.Serializer(name=format)
    for prefix in ns:
        serializer.set_namespace(prefix, RDF.Uri(ns[prefix]))
    serializer.serialize_model_to_file(filename, model)

def main():
    model = createModel()
    mbj_uuid = uuid.uuid4()
    mbj_orcid = "http://orcid.org/0000-0003-0077-4738"
    mbj_data = [mbj_uuid.urn, mbj_orcid]
    personhash = {'Jones, Matthew': mbj_data}
    ns = {
        "foaf": "http://xmlns.com/foaf/0.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "datacite": "http://purl.org/spar/datacite/",
        "owl": "http://www.w3.org/2002/07/owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "geosparql": "http://www.opengis.net/ont/geosparql#",
        "rdfs":  "http://www.w3.org/2000/01/rdf-schema#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "glview": "http://schema.geolink.org/dev/view#"
    }
    xmldoc = getDataList()
    doclist = xmldoc.findall(".//doc")
    print(len(doclist))
    for d in doclist:
        addDataset(model, d, ns, personhash)
        
    print("Model size before serialize: " + str(model.size()))
    serialize(model, ns, "dataone-example-lod.ttl", "turtle")
    serialize(model, ns, "dataone-example-lod.rdf", "rdfxml")

if __name__ == "__main__":
    import RDF
    import urllib2
    import xml.etree.ElementTree as ET
    import uuid
    main()
