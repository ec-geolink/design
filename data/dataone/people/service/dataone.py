""" dataone.py

    Functions related to querying the DataOne v1 API.
"""


from service import util


def getNumResults(query):
    """ Performs a query and extracts just the number of results in the query.
    """

    num_results = -1

    xmldoc = util.getXML(query)
    result_node = xmldoc.findall(".//result")

    if result_node is not None:
        num_results = result_node[0].get('numFound')

    return int(num_results)


def createSinceQuery(from_string, to_string, start=0, page_size=1000):
    """ Creates a query string to get documents uploaded since `from_string` up
        to `to_string`.
    """

    # Create the URL
    base_url = "https://cn.dataone.org/cn/v1/query/solr/"
    fields = ",".join(["identifier"])
    query_params = "formatType:METADATA+AND+(datasource:*LTER+OR+datasource:*"\
                   "KNB+OR+datasource:*PISCO+OR+datasource:*GOA)+AND+-"\
                   "obsoletedBy:*"

    query_params += "+AND+dateModified:[" +\
                    from_string +\
                    "%20TO%20" +\
                    to_string +\
                    "]"

    rows = page_size
    start = start

    query_string = "%s?fl=%s&q=%s&rows=%s&start=%s" % (base_url,
                                                       fields,
                                                       query_params,
                                                       rows,
                                                       start)

    return query_string


def getDocumentIdentifiersSince(from_string, to_string, page_size=1000):
    """ Get document identifiers for documents uploaded since `since`

        since: String of form '2015-05-30T23:21:15.567Z'
    """

    # Get the number of pages we need
    query_string = createSinceQuery(from_string, to_string)
    num_results = getNumResults(query_string)

    # Calculate the number of pages we need to get to get all results
    num_pages = num_results / page_size
    if num_results % page_size > 0:
        num_pages += 1

    print "Found %d documents over %d pages." % (num_results, num_pages)
    # util.continue_or_quit()

    # Collect the identifiers
    identifiers = []

    for page in range(1, num_pages + 1):
        page_identifiers = getIdentifiers(from_string, to_string, page)
        identifiers += page_identifiers

    return identifiers


def getIdentifiers(from_string, to_string, page, page_size=1000):
    """ Query page `page` of the Solr index using and retrieve the PIDs
        of the documents in the response.
    """
    start = (page-1) * page_size
    query_string = createSinceQuery(from_string, to_string, start)

    query_xml = util.getXML(query_string)

    identifiers = query_xml.findall(".//str[@name='identifier']")

    if identifiers is None:
        return []

    identifier_strings = []

    for identifier in identifiers:
        if identifier.text is not None:
            print identifier.text
            identifier_strings.append(identifier.text)

    return identifier_strings


def getDocument(identifier):
    """ Get XML document (sysmeta) at `identifier`"""

    query_string = "http://cn.dataone.org/cn/v1/object/%s" % identifier
    query_xml = util.getXML(query_string)

    return query_xml
