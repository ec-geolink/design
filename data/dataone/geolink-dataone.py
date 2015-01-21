#!/opt/local/bin/python
#
# A quick demo script showing generation of GeoLink RDF from DataONE data sets for a Linked Open Data demo
# See http://schema.geolink.org for schema and namespace details
# See http://releases.dataone.org/online/api-documentation-v1.2.0/ for details of the DataONE API
#
# Matt Jones, NCEAS 2015

def getDataList():
    d1query = "https://cn.dataone.org/cn/v1/query/solr/?fl=identifier,title,author,authorLastName,origin,submitter,rightsHolder,relatedOrganizations,contactOrganization,documents,resourceMap&q=formatType:METADATA&rows=100&start=20000"
    res = urllib2.urlopen(d1query)
    content = res.read()
    xmldoc = ET.fromstring(content)
    return(xmldoc)

def addStatement(model, s, p, o):
    statement=RDF.Statement(RDF.Uri(s),
                        RDF.Uri(p),
                        RDF.Node(o))
    if statement is None:
        raise Exception("new RDF.Statement failed")
    model.add_statement(statement)
    
def addDataset(model, doc):
    d1base = "https://cn.dataone.org/cn/v1/object/"
    dcterms = "http://purl.org/dc/terms/"
    gldataset = "http://schema.geolink.org/repository-object#"
    element = d.find("./str[@name='identifier']")
    identifier = element.text
    addStatement(model, d1base+identifier, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", gldataset+"DigitalObjectRecord")
    addStatement(model, d1base+identifier, dcterms+"identifier", identifier)
    element = d.find("./str[@name='title']")
    title = element.text
    addStatement(model, d1base+identifier, dcterms+"title", title)
    originlist = d.findall("./arr[@name='origin']/str")

def createModel():
    storage=RDF.Storage(storage_name="hashes", name="geolink", options_string="new='yes',hash-type='memory',dir='.'")
    if storage is None:
        raise Exception("new RDF.Storage failed")
    model=RDF.Model(storage)
    if model is None:
        raise Exception("new RDF.model failed")
    return model

def serialize(filename):
    serializer=RDF.Serializer()
    serializer.set_namespace("dcterms", RDF.Uri(dcterms))
    serializer.serialize_model_to_file(filename, model)

def main():
    model = createModel()
    xmldoc = getDataList()
    doclist = xmldoc.findall(".//doc")
    for d in doclist:
        addDataset(model, d)
        #print(ET.tostring(d))
        
    for s in model.find_statements(RDF.Statement()):
        print "found statement:",s
    print "Done"

if __name__ == "__main__":
    import RDF
    import urllib2
    import xml.etree.ElementTree as ET
    main()
