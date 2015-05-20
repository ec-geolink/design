#!/opt/local/bin/python
#
# A quick demo script showing generation of GeoLink-ish RDF from DataONE data sets for a Linked Open Data demo
# See http://schema.geolink.org for schema and namespace details
# See http://releases.dataone.org/online/api-documentation-v1.2.0/ for details of the DataONE API
#
# Matt Jones, NCEAS 2015

def getDataList():
    d1query = "https://cn.dataone.org/cn/v1/query/solr/?fl=identifier,title,abstract,author,authorLastName,origin,submitter,rightsHolder,documents,resourceMap,authoritativeMN&q=formatType:METADATA+AND+(datasource:*LTER+OR+datasource:*KNB+OR+datasource:*PISCO)+AND+-obsoletedBy:*&rows=2000&start=0"
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
    #print(statement)
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
    if (title_element is not None):
        addStatement(model, d1base+identifier, ns["glview"]+"title", title_element.text)

    # Abstract
    abstract_element = doc.find("./str[@name='abstract']")
    if (abstract_element is not None):
        addStatement(model, d1base+identifier, ns["glview"]+"description", abstract_element.text)

    # Creators
    glpeople = loadPeople()
    #table = string.maketrans("","")
    table = {ord(c): None for c in string.punctuation}
    originlist = doc.findall("./arr[@name='origin']/str")
    for creatornode in originlist:
        creator = creatornode.text
        if (creator not in personhash):
            # Add it
            newid = uuid.uuid4()
            p_uuid = newid.hex
            p_orcid = "http://myfakeorcid.org/" + newid.hex
            p_data = [p_uuid, p_orcid]
            personhash[creator] = p_data
        else:
            # Look it up
            p_data = personhash[creator]
            p_uuid = p_data[0]
            p_orcid = p_data[1]
            
        # Person
        person_blank_node = RDF.Node(blank=p_uuid)
        addStatement(model, person_blank_node, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", RDF.Uri(ns["glview"]+"Person"))
        addStatement(model, person_blank_node, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", RDF.Uri(ns["foaf"]+"Person"))
        #addStatement(model, person_blank_node, ns["foaf"]+"name", creator)
        addStatement(model, person_blank_node, ns["glview"]+"nameFull", creator)
        addStatement(model, RDF.Uri(d1base+identifier), RDF.Uri(ns["glview"]+"hasParticipant"), person_blank_node)
        addStatement(model, RDF.Uri(d1base+identifier), RDF.Uri(ns["dcterms"]+"creator"), person_blank_node)
        
        # Match GeoLink Persons
        print "Processing: ", creator
        c_fields = unicode(creator).split()
        normal_creator = c_fields[0].translate(table) + '.*' + c_fields[len(c_fields)-1].translate(table)
        #normal_creator = creator.translate(table, string.punctuation).replace(' ', '.*')
        print "    Lookup: ", normal_creator
        searchRegex = re.compile('('+normal_creator+')').search
        k = findRegexInList(ppl.keys(),searchRegex)
        if (k):
            addStatement(model, person_blank_node, RDF.Uri(ns["glview"]+"matches"), RDF.Uri(glpeople[k[0]]))

        #pi_node = RDF.Node(RDF.Uri(p_orcid))
        #addStatement(model, pi_node, RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), RDF.Uri(ns["datacite"]+"PersonalIdentifier"))       
        #addStatement(model, pi_node, RDF.Uri(ns["datacite"]+"usesIdentifierScheme"), RDF.Uri(ns["datacite"]+"orcid"))       
        #addStatement(model, RDF.Uri(p_uuid), RDF.Uri(ns["datacite"]+"hasIdentifier"), pi_node)

        # ORCID
        #pi_node = RDF.Node(RDF.Uri(p_orcid))
        #addStatement(model, pi_node, RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), RDF.Uri(ns["datacite"]+"PersonalIdentifier"))       
        #addStatement(model, pi_node, RDF.Uri(ns["datacite"]+"usesIdentifierScheme"), RDF.Uri(ns["datacite"]+"orcid"))       
        #addStatement(model, RDF.Uri(p_uuid), RDF.Uri(ns["datacite"]+"hasIdentifier"), pi_node)
        model.sync()


    # TODO: Add Submitters

    # TODO: Add Rights holders

    # Repository
    authMN = doc.find("./str[@name='authoritativeMN']")
    addStatement(model, d1base+identifier, ns["glview"]+"hasRepository", authMN.text)
    model.sync()

    # TODO: Add Landing page
    # TODO: Add Funding
    # TODO: Add MeasurementType

    # Data Objects
    data_list = doc.findall("./arr[@name='documents']/str")
    for data_id_node in data_list:
        data_id = data_id_node.text
        addStatement(model, d1base+data_id, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", RDF.Uri(ns["glview"]+"DigitalObject"))
        addStatement(model, d1base+data_id, ns["glview"]+"isPartOf", RDF.Uri(d1base+identifier))
        # TODO: Add Checksum
        # TODO: Add Size
        # TODO: Add Format
    model.sync()

def findRegexInList(list,filter):
        return [ l for l in list for m in (filter(l),) if m]

def loadPeople():
    # Read in a CSV file of Geolink URIs for people
    with open('../geolink/data.geolink.org-id-person.20150518.csv', 'rb') as csvfile:
        table = string.maketrans("","")
        
        reader = csv.reader(csvfile)
        #for rows in reader:
            #print rows[2], ' |###| ', rows[1]
            #mydict = {(rows[2].split())[0] +'.*'+rows[1]:rows[0]}
        mydict = {(rows[2].split())[0].translate(table, string.punctuation)+' '+rows[1]:rows[0] for rows in reader}
        #mydict = {rows[1]+'.*'+rows[0]:rows[2] for rows in reader}
        csvfile.close()
        return(mydict)

def createModel():
    storage=RDF.Storage(storage_name="hashes", name="geolink", options_string="new='yes',hash-type='memory',dir='.'")
    #storage=RDF.MemoryStorage()
    if storage is None:
        raise Exception("new RDF.Storage failed")
    model=RDF.Model(storage)
    if model is None:
        raise Exception("new RDF.model failed")
    return model

def addRepositories(model, ns):
    node_hash = {}
    d1query = "https://cn.dataone.org/cn/v1/node"
    res = urllib2.urlopen(d1query)
    content = res.read()
    xmldoc = ET.fromstring(content)
    nodelist = xmldoc.findall(".//node")
    for n in nodelist:
        node_id = n.find('identifier').text
        node_name = n.find('name').text
        node_desc = n.find('description').text
        node_base_url = n.find('baseURL').text
        node_hash[node_id] = [node_name, node_desc, node_base_url]
        addStatement(model, node_id, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", RDF.Uri(ns["glview"]+"Repository"))
        addStatement(model, node_id, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", RDF.Uri(ns["glview"]+"Organization"))
        addStatement(model, node_id, RDF.Uri(ns["foaf"]+"name"), node_name)
        addStatement(model, node_id, RDF.Uri(ns["glview"]+"description"), node_desc)
    return(node_hash)

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
    nodes = addRepositories(model, ns)
    xmldoc = getDataList()
    doclist = xmldoc.findall(".//doc")
    print(len(doclist))
    for d in doclist:
        None
        addDataset(model, d, ns, personhash)
        
    print("Model size before serialize: " + str(model.size()))
    serialize(model, ns, "dataone-example-lod.ttl", "turtle")
    serialize(model, ns, "dataone-example-lod.rdf", "rdfxml")

if __name__ == "__main__":
    import RDF
    import urllib2
    import xml.etree.ElementTree as ET
    import uuid
    import re
    import csv
    import string
    #main()
