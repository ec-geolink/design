""" util.py

    Functions offering utility to other functions in this package.
"""

import os
import sys
import xml.etree.ElementTree as ET
import urllib2
import json


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
