""" util.py

    Functions offering utility to other functions in this package.
"""

import os
import sys
import xml.etree.ElementTree as ET
import urllib2
import json
import pandas


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


def loadJSONFile(filename):
    """ Loads as a JSON file as a Python dict.
    """

    content = {}

    if not os.path.exists(filename):
        return content

    with open(filename, "rb") as content_file:
        try:
            content = json.load(content_file)
        except ValueError:
            content = {}

    return content


def saveJSONFile(content, filename):
    """ Saves a dict to a JSON file located at filename.
    """

    with open(filename, "wb") as content_file:
        content_file.write(json.dumps(content,
                            sort_keys=True,
                            indent=2,
                            separators=(',', ': ')))


def ns_interp(text, ns=None):
    """
    Triple strings (e.g. foo:Bar) have to be expanded because SPARQL queries
    can't handle the subject of a triple being

        d1resolve:doi:10.6073/AA/knb-lter-pie.77.3

    but can handle

        <https://cn.dataone.org/cn/v1/resolve/doi:10.6073/AA/knb-lter-pie.77.3>

    This method does that interpolation using the class instance's
    namespaces.

    Returns:
        String, either modified or not.
    """

    if ns is None:
        return text

    colon_index = text.find(":")

    if len(text) <= colon_index + 1:
        return text

    namespace = text[0:colon_index]
    rest = text[(colon_index)+1:]

    if namespace not in ns:
        return text

    return "<%s%s>" % (ns[namespace], rest)


def loadFormatsMap():
    """
    Gets the formats map from GitHub. These are the GeoLink URIs for the
    file format types DataOne knows about.

    Returns:
        A Dict of formats, indexed by format ID.
    """

    formats_table = pandas.read_csv("https://raw.githubusercontent.com/ec-geolink/design/master/data/dataone/formats/formats.csv")

    formats_map = {}

    for row_num in range(formats_table.shape[0]):
        fmt_id = formats_table['id'][row_num]
        fmt_name = formats_table['name'][row_num]
        fmt_type = formats_table['type'][row_num]
        fmt_uri = formats_table['uri'][row_num]

        formats_map[fmt_id] = { 'name': fmt_name, 'type': fmt_type, 'uri': fmt_uri }

    return formats_map


def createIdentifierMap(path):
    """
    Converts a CSV of identifier<->filename mappings into a Dict.

    Returns:
        Dict of identifier<->filename mappings
    """

    identifier_map = None # Will be a docid <-> PID map

    if os.path.isfile(path):
        print "Loading identifiers map..."

        identifier_table = pandas.read_csv(path)
        identifier_map = dict(zip(identifier_table.guid, identifier_table.filepath))

    return identifier_map
