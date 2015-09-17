"""
    file: get_new_datasets.py
    author: Bryce Meucm

    Gets identifiers, system metadata, and science metadata from the DataOne CN
    which have been uploaded since the provided datetime.
"""

import os
import sys
import datetime
import json
import xml.etree.ElementTree as ET
import urllib2


def getNumResults(query):
    """ Performs a query and extracts just the number of results in the query.
    """

    num_results = -1

    xmldoc = getXML(query)
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

    query_params += "+AND+dateUploaded:[" +\
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


def getDocumentsSince(from_string, to_string, page_size=1000):
    """ Get documents uploaded since `since`

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
    continue_or_quit()

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

    query_xml = getXML(query_string)

    identifiers = query_xml.findall(".//str[@name='identifier']")

    if identifiers is None:
        return []

    identifier_strings = []

    for identifier in identifiers:
        if identifier.text is not None:
            print identifier.text
            identifier_strings.append(identifier.text)

    return identifier_strings


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


def initializeSettings(filename):
    """ Read in settings from json file located at `filename` and return
        a Dict of settings.
    """

    settings = {}

    if not os.path.exists(filename):
        return settings

    with open(filename, "rb") as settings_file:
        try:
            settings = json.load(settings_file)
        except ValueError:
            settings = {}

    return settings


def saveSettings(settings, filename):
    """ Save settings in Dict `settings` to json file located at `filename`
    """

    with open(filename, "wb") as settings_file:
        settings_file.write(json.dumps(settings,
                            sort_keys=True,
                            indent=2,
                            separators=(',', ': ')))


def continue_or_quit():
    """ Allows the program to pause in order to ask the user to
    continue or quit."""

    response = None

    while response is None:
        response = raw_input("c(ontinue) or q(uit)")

        if response != "c" and response != "q":
            response = None

    if response == "c":
        print "Continuing..."

    if response == "q":
        print "Exiting..."
        sys.exit()


def main():
    # Settings
    settings = initializeSettings('settings.json')

    if 'last_run' not in settings:
        print "Last run datetime not found in settings.json. Exiting."
        sys.exit()

    # Create from and to strings
    from_string = settings['last_run']
    to_string = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S.0Z")

    # Get documents
    documents = getDocumentsSince(from_string, to_string)
    settings['last_run'] = to_string

    # Save settings
    saveSettings(settings, 'settings.json')

    return


if __name__ == "__main__":
    main()
