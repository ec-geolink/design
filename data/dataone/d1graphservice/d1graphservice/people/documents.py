"""
    file: documents.py
    author: Bryce Meucm

    Gets n scimeta documents off the D1 Solr index and saves them in a
    subdirectory.
"""


def getDocuments(n=100, start=0):
    """Get `n`, staring at `start` documents off the CN's Solr index."""

    base_url = "https://cn.dataone.org/cn/v1/query/solr/"
    fields = ",".join(["identifier"])
    query_params = "formatType:METADATA+AND+(datasource:*LTER+OR+datasource:*"\
                   "KNB+OR+datasource:*PISCO+OR+datasource:*GOA)+AND+-"\
                   "obsoletedBy:*"
    rows = n
    start = start

    query_string = "%s?fl=%s&q=%s&rows=%s&start=%s" % (base_url,
                                                       fields,
                                                       query_params,
                                                       rows,
                                                       start)
    print(query_string)

    xmldoc = getXML(query_string)

    return(xmldoc)


def getSysMeta(identifier):
    """Get the system metadata for document `identifier`"""

    getDocumentAtEndpoint("meta", identifier)


def getSciMeta(identifier):
    """Get the scientific metadata for document `identifier`"""

    getDocumentAtEndpoint("resolve", identifier)


def getDocumentAtEndpoint(endpoint, identifier):
    """Helper function to get a document at an arbitrary REST endpoint"""

    base_url = "https://cn.dataone.org/cn/v1"

    query_string = "%s/%s/%s" % (base_url,
                                 endpoint,
                                 urllib.quote_plus(identifier))
    print("\t" + query_string)

    xmldoc = getXML(query_string)

    return(xmldoc)


def getXML(url):
    """Get XML document at the given url `url`"""

    try:
        res = urllib2.urlopen(url)
    except:
        print "\tgetXML failed for %s" % url
        return None

    content = res.read()
    xmldoc = ET.fromstring(content)

    return(xmldoc)


def saveXML(filename, xmldoc):
    """Save a pretty-printed version of an XML document"""

    xmlstr = minidom.parseString(ET.tostring(xmldoc)).toprettyxml(indent="\t")

    filename_with_path = "./documents/%s" % filename
    with codecs.open(filename_with_path, "w", encoding="utf-8") as f:
        f.write(xmlstr)


def main(n, start):
    results = getDocuments(n)

    documents = results.findall(".//str[@name='identifier']")

    identifiers = []

    for document in documents:
        identifiers.append(document.text)

    for identifier in identifiers:
        filename = identifier.translate(None, "/:")

        print "%s" % (identifier)

        scimeta = getSciMeta(identifier)

        # Bail if we can't get scimeta
        if scimeta is None:
            print "\tCoudln't get scimeta for %s." % (identifier)
            continue

        sysmeta = getSysMeta(identifier)

        if sysmeta is not None:
            saveXML("%s-sysmeta.xml" % filename, sysmeta)

        saveXML("%s-scimeta.xml" % filename, scimeta)


if __name__ == "__main__":
    import urllib2
    import urllib
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    import os
    import codecs
    if not os.path.exists("./documents"):
        os.makedirs("./documents")

    n = 100
    start = 30000

    main(n, start)
