#!/opt/local/bin/python
#
# A quick demo script showing generation of GeoLink-ish RDF from DataONE data sets for a Linked Open Data demo
# See http://schema.geolink.org for schema and namespace details
# See http://releases.dataone.org/online/api-documentation-v1.2.0/ for details of the DataONE API
#
# Matt Jones, NCEAS 2015


def getDataList(page, pagesize):
    start = (page-1)*pagesize
    fields = ",".join(["identifier","title","abstract","author",
    "authorLastName", "origin","submitter","rightsHolder","documents",
    "resourceMap","authoritativeMN","obsoletes","northBoundCoord",
    "eastBoundCoord","southBoundCoord","westBoundCoord","startDate","endDate",
    "datasource","replicaMN"])

    d1query = "https://cn.dataone.org/cn/v1/query/solr/?fl=" + fields + "&q=formatType:METADATA+AND+(datasource:*LTER+OR+datasource:*KNB+OR+datasource:*PISCO+OR+datasource:*GOA)+AND+-obsoletedBy:*&rows="+str(pagesize)+"&start="+str(start)
    print(d1query)
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
    repo_base = "https://cn.dataone.org/cn/v1/node/"  # For MN URIs

    # Identifier and Dataset
    element = doc.find("./str[@name='identifier']")
    identifier = element.text

    addStatement(model, d1base+identifier, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["glbase"]+"Dataset"))

    # Identifier

    # Determine identifier scheme
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

    # Add glview Identifier
    id_blank_node_glbase = RDF.Node(blank=identifier)

    addStatement(model, id_blank_node_glbase, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["glbase"]+"Identifier"))
    addStatement(model, id_blank_node_glbase, ns["glbase"]+"hasIdentifierValue", identifier)
    addStatement(model, id_blank_node_glbase, ns["rdfs"]+"label", identifier)
    addStatement(model, id_blank_node_glbase, ns["glbase"]+"hasIdentifierScheme", RDF.Uri(ns["datacite"]+scheme))

    addStatement(model, d1base+identifier, ns["glbase"]+"hasIdentifier", id_blank_node_glbase)

    # Add datacite ResourceIdentifier (optional)
    # id_blank_node_datacite = RDF.Node(blank=identifier)
    #
    # # DataCite prefers DOIs to be a PrimaryResourceIdentifier
    # if scheme is 'doi':
    #     addStatement(model, id_blank_node_datacite, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["datacite"]+"PrimaryResourceIdentifier"))
    # else:
    #     addStatement(model, id_blank_node_datacite, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["datacite"]+"AlternativeResourceIdentifier"))
    #
    # addStatement(model, id_blank_node_datacite, ns["rdfs"]+"label", identifier)
    # addStatement(model, id_blank_node_datacite, ns["literal"]+"hasLiteralValue", identifier)
    # addStatement(model, id_blank_node_datacite, ns["glbase"]+"usesIdentifierScheme", RDF.Uri(ns["datacite"]+scheme))
    #
    # addStatement(model, d1base+identifier, ns["glbase"]+"hasIdentifier", id_blank_node_datacite)


    # Title
    title_element = doc.find("./str[@name='title']")
    if (title_element is not None):
        addStatement(model, d1base+identifier, ns["glbase"]+"title", title_element.text)
        addStatement(model, d1base+identifier, ns["rdfs"]+"label", title_element.text)

    # Abstract
    abstract_element = doc.find("./str[@name='abstract']")
    if (abstract_element is not None):
        addStatement(model, d1base+identifier, ns["glbase"]+"description", abstract_element.text)

    # Creators

    # mecum: This is a little more complex than initially coded up.
    # The <origin> tag can hold complex information of multiple forms. First, origin can
    # be a person /or/ an organization, though neither are labeled explictly as one or the other.
    # Additionally, a person /and/ and organization can be found in the <origin> tag, e.g.:
    #
    #   - Daniel Childers||Global Institute of Sustainability| School of Sustainability
    #   - John Connors, HERO-CM
    #   - ARC
    #   - Peter Groffman , Email: groffmanp@ecostudies.org
    #   - SANParks
    #   - National Climatic Data Center (NCDC) NOAA
    #   - Tene Fossog, Billy
    #   - Intergovernmental Panel on Climate Change (IPCC)
    #   - Sawaya, Michael A.

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
            addStatement(model, person_node, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["glbase"]+"Person"))
            addStatement(model, person_node, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["foaf"]+"Person"))
            addStatement(model, person_node, ns["rdfs"]+"label", c_text)
            addStatement(model, person_node, ns["foaf"]+"name", c_text)
            addStatement(model, person_node, ns["glbase"]+"nameFull", c_text)

            # Match GeoLink Persons
            print 'c',
            sys.stdout.flush()
            normal_creator = c_fields[0].translate(table) + '.*' + c_fields[len(c_fields)-1].translate(table)

            # print c_text, " |###| ", normal_creator
            searchRegex = re.compile('('+normal_creator+')').search
            k = None
            k = findRegexInList(glpeople.keys(),searchRegex)
            if (k):
                addStatement(model, person_node, RDF.Uri(ns["glbase"]+"matches"), RDF.Uri(glpeople[k[0]]))

            p_data = [p_uuid, p_dataone_id, person_node]
            personhash[creator] = p_data
        else:
            # Look it up
            p_data = personhash[creator]
            p_uuid = p_data[0]
            p_dataone_id = p_data[1]
            person_node = p_data[2]

        # Add Person as creator participant in Dataset
        addStatement(model, RDF.Uri(d1base+identifier), RDF.Uri(ns["glbase"]+"hasCreator"), person_node)
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



    # Spatial Coverage
    # Implementing this as hasGeometryAsWktLiteral

    bound_north = doc.find("./float[@name='northBoundCoord']")
    bound_east = doc.find("./float[@name='eastBoundCoord']")
    bound_south = doc.find("./float[@name='southBoundCoord']")
    bound_west = doc.find("./float[@name='westBoundCoord']")

    if all(ele is not None for ele in [bound_north, bound_east, bound_south, bound_west]):

        if bound_north.text == bound_south.text and bound_west.text == bound_east.text:
            wktliteral = "POINT (%s %s)" % (bound_north.text, bound_east.text)
        else:
            wktliteral = "POLYGON ((%s %s, %s %s, %s %s, %s, %s))" % (bound_west.text, bound_north.text, bound_east.text, bound_north.text, bound_east.text, bound_south.text, bound_west.text, bound_south.text)

        addStatement(model, d1base+identifier, ns['glbase'] + "hasGeometryAsWktLiteral", wktliteral)



    # Temporal Coverage
    # TODO: No field for these in glbase, currently exist in doview

    start_date = doc.find("./date[@name='startDate']")

    if start_date is not None:
        addStatement(model, d1base+identifier, ns["doview"]+"hasStartDate", start_date.text)


    end_date = doc.find("./date[@name='endDate']")

    if end_date is not None:
        addStatement(model, d1base+identifier, ns["doview"]+"hasEndDate", end_date.text)


    # Submitter
    submitter = doc.find("./str[@name='submitter']")

    # TODO: Make this point to a Person
    addStatement(model, d1base+identifier, ns["glbase"]+"hasCreator", RDF.Uri("TODO"))


    # Add Rights holder
    rights_holder = doc.find("./str[@name='rightsHolder']")

    # TODO: Make this point to an Organization or Person
    addStatement(model, d1base+identifier, ns["glbase"]+"hasRightsHolder", RDF.Uri("TODO"))


    # Repositories: authoritative, replica, origin

    # Authoritative MN
    repository_authMN = doc.find("./str[@name='authoritativeMN']")
    addStatement(model, d1base+identifier, ns["doview"]+"hasAuthoritativeDigitalRepository", RDF.Uri(repo_base + repository_authMN.text))

    # Replica MN's
    repository_replicas = doc.findall("./arr[@name='replicaMN']/str")

    for repo in repository_replicas:
        addStatement(model, d1base+identifier, ns["doview"]+"hasReplicaDigitalRepository", RDF.Uri(repo_base + repo.text))

    # Origin MN
    repository_datasource = doc.find("./str[@name='datasource']")
    addStatement(model, d1base+identifier, ns["doview"]+"hasOriginDigitalRepository", RDF.Uri(repo_base + repository_datasource.text))

    # TODO: Add Landing page
    """ Landing page:
        Use search.dataone.org/#view/{PID}
    """

    addStatement(model, d1base+identifier, ns['doview']+'hasLandingPage', 'https://search.dataone.org/#view/'+identifier)


    # TODO: Add Funding

    # TODO: Add MeasurementType

    # Obsoletes as PROV#wasRevisionOf
    obsoletes_node = doc.find("./str[@name='obsoletes']")

    if obsoletes_node is not None:
        addStatement(model, d1base+identifier, ns['prov']+"wasRevisionOf", RDF.Uri(d1base + obsoletes_node.text))

    # Data Objects
    data_list = doc.findall("./arr[@name='documents']/str")

    for data_id_node in data_list:
        addDigitalObject(model, d1base, identifier, data_id_node, ns, fm, personhash)


    model.sync()


def addDigitalObject(model, d1base, identifier, data_id_node, ns, fm, personhash):
    data_id = data_id_node.text

    addStatement(model, d1base+data_id, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["glbase"]+"DigitalObject"))
    addStatement(model, d1base+data_id, ns["glbase"]+"isPartOf", RDF.Uri(d1base+identifier))

    # Get data object meta
    data_meta = getXML("https://cn.dataone.org/cn/v1/meta/" + data_id)

    if data_meta is None:
        print "Metadata for data object %s was not found. Continuing to next data object." % data_id
        return


    # Checksum and checksum algorithm
    checksum_node = data_meta.find(".//checksum")

    if checksum_node is not None:
        addStatement(model, d1base+data_id, ns["glbase"]+"hasChecksum", checksum_node.text )
        addStatement(model, d1base+data_id, ns["doview"]+"hasChecksumAlgorithm", checksum_node.get("algorithm"))


    # Size
    size_node = data_meta.find("./size")

    if size_node is not None:
        addStatement(model, d1base+data_id, ns["glbase"]+"hasByteLength", size_node.text)


    # Format
    format_id_node = data_meta.find("./formatId")

    if format_id_node is not None:
        if format_id_node.text in fm:
            addStatement(model, d1base+data_id, ns["glbase"]+"hasFormat", RDF.Uri(fm[format_id_node.text]))
        else:
            print "Format not found."


    # Date uploaded
    date_uploaded_node = data_meta.find("./dateUploaded")

    if date_uploaded_node is not None:
        addStatement(model, d1base+data_id, ns["doview"]+"dateUploaded", date_uploaded_node.text)

    # Submitter and rights holders
    submitter_node = data_meta.find("./submitter")

    if submitter_node is not None:
        submitter_node_text = " ".join(re.findall(r"o=(\w+)", submitter_node.text, re.IGNORECASE))

        if len(submitter_node_text) > 0:
            addStatement(model, d1base+data_id, ns["glbase"]+"hasCreator", RDF.Uri(ns['d1node'] + submitter_node_text.upper()))


    rights_holder_node = data_meta.find("./rightsHolder")

    if rights_holder_node is not None:
        rights_holder_node_text = " ".join(re.findall(r"o=(\w+)", rights_holder_node.text, re.IGNORECASE))

        if len(rights_holder_node_text) > 0:
            addStatement(model, d1base+data_id, ns["glbase"]+"hasRightsHolder", RDF.Uri("urn:node:" + rights_holder_node_text.upper()))


def findRegexInList(list,filter):
        return [ l for l in list for m in (filter(l),) if m]


def loadFormats(ns):
    fm = {}

    with open("./formats/formats.csv", "rb") as f:
        reader = csv.reader(f)

        for row in reader:
            fm[row[0]] = row[1]

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
    # storage=RDF.Storage(storage_name="file", name="geolink", options_string="new='yes',hash-type='memory',dir='.'")

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
    xmldoc = getXML(d1query)

    if xmldoc is None:
        return node_hash

    repo_base = "https://cn.dataone.org/cn/v1/node/"
    nodelist = xmldoc.findall(".//node")

    for n in nodelist:
        node_id = ns['d1node'] + n.find('identifier').text
        node_name = n.find('name').text
        node_desc = n.find('description').text
        node_base_url = n.find('baseURL').text

        node_hash[node_id] = [node_name, node_desc, node_base_url]

        addStatement(model, repo_base + node_id, RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["glbase"]+"Repository"))
        addStatement(model, repo_base + node_id, RDF.Uri(ns["foaf"]+"name"), node_name)
        addStatement(model, repo_base + node_id, RDF.Uri(ns["rdfs"]+"label"), node_name)
        addStatement(model, repo_base + node_id, RDF.Uri(ns["glbase"]+"description"), node_desc)

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

        addStatement(model, fm[format_id], RDF.Uri(ns["rdf"]+"type"), RDF.Uri(ns["glbase"]+"Format"))
        addStatement(model, fm[format_id], RDF.Uri(ns["glbase"]+"hasIdentifier"), format_id)
        addStatement(model, fm[format_id], RDF.Uri(ns["glbase"] + "description"), format_name)


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


def processPage(model, ns, fm, personhash, page, pagesize=1000):
    xmldoc = getDataList(page, pagesize)

    sys.exit()
    if xmldoc is None:
        print "Failed to retrieve page from the Solr index. Exiting."
        sys.exit()

    resultnode = xmldoc.findall(".//result")
    num_results = resultnode[0].get('numFound')
    doclist = xmldoc.findall(".//doc")

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
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "glbase": "http://schema.geolink.org/dev/base/main#",
        "doview": "http://schema.geolink.org/dev/doview#",
        "prov": "http://www.w3.org/ns/prov#",
        "d1node": "https://cn.dataone.org/cn/v1/node/",
        "literal": "http://www.essepuntato.it/2010/06/literalreification/"
    }

    print "Creating format map..."
    fm = loadFormats(ns)

    nodes = addRepositories(model, ns)
    formats = addFormats(model, ns, fm)

    pagesize = 50
    print "Processing page: 1",
    records = processPage(model, ns, fm, personhash, 1, pagesize=pagesize )
    # if (records > pagesize):
    #     print str(model.size())
    #     sys.stdout.flush()
    #     numpages = records/pagesize+1
    #     for page in range(2,numpages+1):
    #         print "Processing page: ",page," of ",numpages,
    #         processPage(model, ns, personhash, page, pagesize=pagesize )
    #         print str(model.size())
    #         sys.stdout.flush()
    #         serialize(model, ns, "dataone-example-lod.ttl", "turtle")

    print("Final model size: " + str(model.size()))
    serialize(model, ns, "datasets.ttl", "turtle")
    # serialize(model, ns, "dataone-example-lod.rdf", "rdfxml")

if __name__ == "__main__":
    import RDF
    import urllib2
    import xml.etree.ElementTree as ET
    import uuid
    import re
    import csv
    import string
    import sys

    # main()
    getDataList(1, 100)
