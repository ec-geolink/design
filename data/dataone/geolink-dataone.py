#!/opt/local/bin/python
#
# A quick demo script showing generation of GeoLink-ish RDF from DataONE data sets for a Linked Open Data demo
# See http://schema.geolink.org for schema and namespace details
# See http://releases.dataone.org/online/api-documentation-v1.2.0/ for details of the DataONE API
#
# Matt Jones, NCEAS 2015

def getDataList(page, pagesize):
    start = (page-1)*pagesize
    fields = ",".join(["identifier","title","abstract","author","authorLastName","origin","submitter","rightsHolder","documents","resourceMap","authoritativeMN","obsoletes"])
    
    d1query = "https://cn.dataone.org/cn/v1/query/solr/?fl=" + fields + "&q=identifier:*dpennington*+AND+formatType:METADATA+AND+(datasource:*LTER+OR+datasource:*KNB+OR+datasource:*PISCO+OR+datasource:*GOA)+AND+-obsoletedBy:*&rows="+str(pagesize)+"&start="+str(start)
    xmldoc = getXML(d1query)

    return(xmldoc)

def getXML(url):
    try:
        res = urllib2.urlopen(url)
    except:
        print "getXML failed for %s" % url
        return None

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

def addDataset(model, doc, ns, fm, personhash):
    d1base = "https://cn.dataone.org/cn/v1/resolve/"
    # Identifier and Dataset
    element = doc.find("./str[@name='identifier']")
    identifier = element.text
    addStatement(model, d1base+identifier, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["glview"]+"Dataset"))
    id_blank_node = RDF.Node(blank=identifier)
    addStatement(model, id_blank_node, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["datacite"]+"ResourceIdentifier"))
    addStatement(model, d1base+identifier, ns["glview"]+"identifier", id_blank_node)
    addStatement(model, id_blank_node, ns["glview"]+"hasIdentifierValue", identifier)
    addStatement(model, id_blank_node, ns["rdfs"]+"label", identifier)
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
        addStatement(model, d1base+identifier, ns["rdfs"]+"label", title_element.text)

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
        c_text = creatornode.text
        c_fields = unicode(c_text).split()
        creator = c_fields[0].translate(table) + ' ' + c_fields[len(c_fields)-1].translate(table)
        if (creator not in personhash):
            # Add it
            newid = uuid.uuid4()
            p_uuid = newid.hex
            p_dataone_id = "http://data.geolink.org/id/dataone/" + newid.hex
            person_node = RDF.Uri(p_dataone_id)
            #person_node = RDF.Node(blank=p_uuid)
            addStatement(model, person_node, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["glview"]+"Person"))
            addStatement(model, person_node, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["foaf"]+"Person"))
            addStatement(model, person_node, ns["rdfs"]+"label", c_text)
            addStatement(model, person_node, ns["foaf"]+"name", c_text)
            addStatement(model, person_node, ns["glview"]+"nameFull", c_text)
            
            # Match GeoLink Persons
            print 'c',
            sys.stdout.flush()
            normal_creator = c_fields[0].translate(table) + '.*' + c_fields[len(c_fields)-1].translate(table)
            #print c_text, " |###| ", normal_creator
            searchRegex = re.compile('('+normal_creator+')').search
            k = None
            k = findRegexInList(glpeople.keys(),searchRegex)
            if (k):
                addStatement(model, person_node, RDF.Uri(ns["glview"]+"matches"), RDF.Uri(glpeople[k[0]]))

            p_data = [p_uuid, p_dataone_id, person_node]
            personhash[creator] = p_data
        else:
            # Look it up
            p_data = personhash[creator]
            p_uuid = p_data[0]
            p_dataone_id = p_data[1]
            person_node = p_data[2]
            
        # Add Person as creator participant in Dataset
        addStatement(model, RDF.Uri(d1base+identifier), RDF.Uri(ns["glview"]+"hasCreator"), person_node)
        addStatement(model, RDF.Uri(d1base+identifier), RDF.Uri(ns["dcterms"]+"creator"), person_node)
        
        #pi_node = RDF.Node(RDF.Uri(p_orcid))
        #addStatement(model, pi_node, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["datacite"]+"PersonalIdentifier"))       
        #addStatement(model, pi_node, RDF.Uri(ns["datacite"]+"usesIdentifierScheme"), RDF.Uri(ns["datacite"]+"orcid"))       
        #addStatement(model, RDF.Uri(p_uuid), RDF.Uri(ns["datacite"]+"hasIdentifier"), pi_node)

        # ORCID
        #pi_node = RDF.Node(RDF.Uri(p_orcid))
        #addStatement(model, pi_node, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["datacite"]+"PersonalIdentifier"))       
        #addStatement(model, pi_node, RDF.Uri(ns["datacite"]+"usesIdentifierScheme"), RDF.Uri(ns["datacite"]+"orcid"))       
        #addStatement(model, RDF.Uri(p_uuid), RDF.Uri(ns["datacite"]+"hasIdentifier"), pi_node)

    model.sync()
    print '.', 



    # TODO: Add Spatial Coverage, no field for this in GL View

    # TODO: Add Temporal Coverage, no field for this in GL View

    # TODO: Add Submitters, no field for this in GL View

    # TODO: Add Rights holders

    # Repository
    authMN = doc.find("./str[@name='authoritativeMN']")
    addStatement(model, d1base+identifier, ns["glview"]+"hasRepository", authMN.text)
    model.sync()

    # TODO: Add Landing page

    # TODO: Add Funding

    # TODO: Add MeasurementType

    # Obsoletes as PROV#wasRevisionOf
    obsoletes_node = doc.find("./str[@name='obsoletes']")

    if obsoletes_node is not None:
        addStatement(model, d1base+identifier, ns['prov']+"wasRevisionOf", RDF.Uri(obsoletes_node.text))
    # Data Objects
    data_list = doc.findall("./arr[@name='documents']/str")
    for data_id_node in data_list:
        data_id = data_id_node.text
        addStatement(model, d1base+data_id, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["glview"]+"DigitalObject"))
        addStatement(model, d1base+data_id, ns["glview"]+"isPartOf", RDF.Uri(d1base+identifier))

        # Get data object meta
        data_meta = getXML("https://cn.dataone.org/cn/v1/meta/" + data_id)

        if data_meta is None:
            print "Metadata for data object %s was not found. Continuing to next data object." % data_id
            continue


        # Checksum and checksum algorithm
        checksum_node = data_meta.find(".//checksum")

        if checksum_node is not None:
            addStatement(model, d1base+data_id, ns["glview"]+"hasChecksum", checksum_node.text )
            addStatement(model, d1base+data_id, ns["doview"]+"hasChecksumAlgorithm", checksum_node.get("algorithm"))


        # Size
        size_node = data_meta.find("./size")

        if size_node is not None:
            addStatement(model, d1base+data_id, ns["glview"]+"hasByteLength", size_node.text)


        # Format
        format_id_node = data_meta.find("./formatId")

        if format_id_node is not None:
            addStatement(model, d1base+data_id, ns["glview"]+"hasFormatType", RDF.Uri(format_id_node.text))


        # Date uploaded
        date_uploaded_node = data_meta.find("./dateUploaded")

        if date_uploaded_node is not None:
            addStatement(model, d1base+data_id, ns["doview"]+"dateUploaded", date_uploaded_node.text)

        # Submitter and rights holders
        # TODO: No fields for these in GL View
        submitter_node = data_meta.find("./submitter")
        rights_holder_node = data_meta.find("./rightsHolder")

        if submitter_node is not None:
            addStatement(model, d1base+data_id, ns["doview"]+"hasSubmitter", submitter_node.text)

        if rights_holder_node is not None:
            addStatement(model, d1base+data_id, ns["doview"]+"hasRightsHolder", rights_holder_node.text)


    model.sync()

def findRegexInList(list,filter):
        return [ l for l in list for m in (filter(l),) if m]

def loadFormats(ns):
    fm = {}

    d1_formats = {}
    geolink_formats = {}

    formats_xml_d1 = getXML("https://cn.dataone.org/cn/v1/formats")
    formats_d1 = formats_xml_d1.findall(".//objectFormat")

    for fmt in formats_d1:
        format_id_d1 = fmt.find("./formatId").text
        format_name_d1 = fmt.find("./formatName").text

        d1_formats[format_id_d1] = format_name_d1

    formats_xml_gl = getXML("http://schema.geolink.org/dev/voc/dataone/format.owl")
    formats_gl = formats_xml_gl.findall(".//owl:Class", ns)

    for fmt in formats_gl:
        label_gl = fmt.find("./rdfs:label", ns).text
        uri_gl = fmt.get("{" + ns['rdf'] + "}about")

        geolink_formats[label_gl] = uri_gl

    for d1fmt in d1_formats:
        for glfmt in geolink_formats:
            if d1_formats[d1fmt] in glfmt:
                fm[d1fmt] = geolink_formats[glfmt]

    return fm


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
        addStatement(model, node_id, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["glview"]+"Repository"))
        addStatement(model, node_id, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["glview"]+"Organization"))
        addStatement(model, node_id, RDF.Uri(ns["foaf"]+"name"), node_name)
        addStatement(model, node_id, RDF.Uri(ns["rdfs"]+"label"), node_name)
        addStatement(model, node_id, RDF.Uri(ns["glview"]+"description"), node_desc)
    return(node_hash)


def addFormats(model, ns, fm):
    format_hash = {}

    d1query = "https://cn.dataone.org/cn/v1/formats"
    xmldoc = getXML(d1query)

    if xmldoc is None:
        return

    nodelist = xmldoc.findall(".//objectFormat")

    for n in nodelist:
        format_id = n.find("./formatId").text
        format_name = n.find("./formatName").text
        format_type = n.find("./formatType").text

        format_hash[format_id] = [format_type, format_name]

        if format_id in fm:
            addStatement(model, format_id, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(fm[format_id]))
        else:
            addStatement(model, format_id, RDF.Uri(ns["rdf"]+"type"), format_id)


    return format_hash


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

    xmldoc = getDataList(page, pagesize)
def processPage(model, ns, fm, personhash, page, pagesize=1000):
    resultnode = xmldoc.findall(".//result")
    num_results = resultnode[0].get('numFound')
    doclist = xmldoc.findall(".//doc")
    #print(len(doclist))
    for d in doclist:
        None
        addDataset(model, d, ns, fm, personhash)
    return(int(num_results))

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
        "glview": "http://schema.geolink.org/dev/view#",
        "doview": "http://schema.geolink.org/dev/doview#",
        "prov"  : "http://www.w3.org/ns/prov#"
    }
    
    print "Creating format map..."
    fm = loadFormats(ns)

    nodes = addRepositories(model, ns)
    formats = addFormats(model, ns, fm)

    # Create format maps to map between D1 and GeoLink formats
    pagesize=100
    print "Processing page: 1",
    if (records > pagesize):
        print str(model.size())
        sys.stdout.flush()
        numpages = records/pagesize+1
        for page in range(2,numpages+1):
            print "Processing page: ",page," of ",numpages,
            processPage(model, ns, personhash, page, pagesize=pagesize )
            print str(model.size())
            sys.stdout.flush()
            serialize(model, ns, "dataone-example-lod.ttl", "turtle")
    records = processPage(model, ns, fm, personhash, 1, pagesize=pagesize )

    print("Final model size: " + str(model.size()))
    serialize(model, ns, "dataone-example-lod.ttl", "turtle")
    #serialize(model, ns, "dataone-example-lod.rdf", "rdfxml")

if __name__ == "__main__":
    import RDF
    import urllib2
    import xml.etree.ElementTree as ET
    import uuid
    import re
    import csv
    import string
    import sys
    #main()
