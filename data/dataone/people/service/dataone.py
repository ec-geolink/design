"""
dataone.py

Functions related to querying the DataOne v1 API.
"""


from service import util


def getNumResults(query):
    """
    Performs a query and extracts just the number of results in the query.
    """

    num_results = -1

    xmldoc = util.getXML(query)
    result_node = xmldoc.findall(".//result")

    if result_node is not None:
        num_results = result_node[0].get('numFound')

    return int(num_results)


def createSinceQuery(from_string, to_string, fields=None, start=0, page_size=1000):
    """
    Creates a query string to get documents uploaded since `from_string` up
    to `to_string`.

    Parameters:

        from_string|to_string:
            String of form '2015-05-30T23:21:15.567Z'

        fields: optional
            List of string field names

        start|page_size: optional
            Solr query parameters
    """

    # Create the URL
    base_url = "https://cn.dataone.org/cn/v1/query/solr/"

    # Create a set of fields to grab
    if fields is None:
        fields = ",".join(["identifier"])
    else:
        fields = ",".join(fields)

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


def getDocumentIdentifiersSince(from_string, to_string, fields=None, page_size=1000):
    """
    Get document identifiers for documents uploaded since `since`

    Parameters:
        from_string|to_string:
            String of form '2015-05-30T23:21:15.567Z'
    """

    # Get the number of pages we need
    query_string = createSinceQuery(from_string, to_string, fields, page_size)
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


def getSincePage(from_string, to_string, fields=None, page=1, page_size=1000):
    """
    Get a page off the Solr index for a query between two time periods.
    """

    start = (page-1) * page_size
    query_string = createSinceQuery(from_string, to_string, fields, start, page_size)
    print query_string
    query_xml = util.getXML(query_string)

    return query_xml


def getIdentifiers(from_string, to_string, fields=None, page=1, page_size=1000):
    """
    Query page `page` of the Solr index using and retrieve the PIDs
    of the documents in the response.
    """
    start = (page-1) * page_size
    query_string = createSinceQuery(from_string, to_string, fields, start)

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
    """
    Get XML document (sysmeta) for an identifier.
    """

    query_string = "http://cn.dataone.org/cn/v1/object/%s" % identifier
    query_xml = util.getXML(query_string)

    return query_xml
