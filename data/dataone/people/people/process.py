"""
    file: process_documents.py
    author: Bryce Mecum (mecum@nceas.ucsb.edu)

    Processes the scientific metadata documents in ./documents for person
    and organization information. For each document, the script tries to find
    the person in an existing list. Matches are currently made off of all
    information available but future versions should be more loose about this.

    The document a person/organization was found in are also added to that
    person/organization so the documents belonging to that person/organization
    can be attributed to them and used in later graph generation activities.
"""

import sys
import os
import re
import uuid
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError


def processDirectory(directory):
    # array of dicts with keys first, middle, last, email (all to lowercase)
    people = []
    organizations = []  # array of dicts containing org name, website, and email

    filenames = os.listdir("./%s" % directory)
    # scimeta_docs = [f for f in filenames if re.search("scimeta\.xml$", f)]
    scimeta_docs = filenames

    for xmldoc in scimeta_docs:
        document = uuid.uuid4()

        try:
            xmldoc = ET.parse("%s/%s" % (directory, xmldoc))
        except ParseError:
            print "Couldn't parse document at ./documents/%s. Moving on to the next file." % xmldoc
            continue

        # Check if EML
        root = xmldoc.getroot()

        if not re.search("eml$", root.tag):
            print "Not EML. Moving on to next document."
            continue

        # Process each <creator>
        creators = xmldoc.findall(".//creator")

        for creator in creators:
            people, organizations = processCreator(
                people, organizations, creator, document)

    return people, organizations


def processCreator(people, organizations, creator, document):
    """Process the <creator> tag in an EML document"""

    if creator.find("./individualName") is not None:
        people = processIndividual(people, creator, document)
    elif creator.find("./organizationName") is not None:
        organizations = processOrganization(organizations, creator, document)
    else:
        print "Couldn't find an individual or organization."

    return people, organizations


def processIndividual(people, creator, document):
    """ Proccess a <creator> tag for an individual.

        Processing involves two steps:

            1. Parsing relevant information (e.g. name)
            2. Scoring that information against existing records.
    """

    person = {}

    individual = creator.find("./individualName")

    if individual is not None:
        salutation = individual.find("./salutation")
        given_name = individual.find("./givenName")
        sur_name = individual.find("./surName")

        if salutation is not None:
            title = salutation.text.lower()
            person["title"] = title.translate(None, ".")

        if given_name is not None:
            first_name = given_name.text.lower()

            # First I.
            pattern_one = re.compile("\w+\s+\w{1}\.?")

            # First I. J.
            pattern_two = re.compile("\w+\s+\w{1}\.?\w{1}\.?")

            if pattern_one.match(first_name):
                first_name = first_name.split(" ")

                person["first"] = first_name[0]
                person["middle"] = [first_name[1].translate(None, ".")]
            elif pattern_two.match(first_name):
                first_name = first_name.split(" ")

                person["first"] = first_name[0]
                person["middle"] = [first_name[1].translate(None, "."), first_name[
                    2].translate(None, ".")]
            else:
                person["first"] = first_name

        if sur_name is not None:
            person["last"] = sur_name.text.lower()

    email = creator.find("./electronicMailAddress")

    if email is not None:
        person["email"] = email.text.lower()

    if person:
        scores = findPerson(people, person)

        if not scores:
            print "NOT FOUND. Creating new."
            person["documents"] = [str(document)]

            people.append(person)
        else:
            if len(scores) == 1:  # Single best match
                existing = people[scores.keys()[0]]
                print "MATCH: Single best match"
                print "\t%s" % personString(person)
                print "\t%s" % personString(existing)

                if "documents" in existing:
                    existing["documents"].append(str(document))
                else:
                    existing["documents"] = [str(document)]
            else:
                print "ERROR"

    return people


def processOrganization(organizations, creator, document):
    """ Proccess a <creator> tag for an organization.

        Processing involves two steps:

            1. Parsing relevant information (e.g. name)
            2. Scoring that information against existing records.
    """
    organization = {}

    name = creator.find("./organizationName")
    email = creator.find("./electronicMailAddress")
    url = creator.find("./onlineUrl")

    if name is not None:
        organization["name"] = name.text.lower()

    if email is not None:
        organization["email"] = email.text.lower()

    if url is not None:
        organization["url"] = url.text.lower()

    if organization:
        scores = findOrganization(organizations, organization)

        if not scores:
            print "NOT FOUND: Creating new."
            organization["documents"] = [str(document)]

            organizations.append(organization)
        else:
            if len(scores) == 1:  # Single best match
                existing = organizations[scores.keys()[0]]
                print "MATCH: Single best match"
                print "\t%s" % organizationString(organization)
                print "\t%s" % organizationString(existing)

                if "documents" in existing:
                    existing["documents"].append(str(document))
                else:
                    existing["documents"] = [str(document)]
            else:
                print "ERROR"

    return organizations


def findPerson(people, person):
    """ Find and score a `person` within `people`"""

    print "FIND[PERSON](%s)" % personString(person)

    scores = {}

    for i in range(0, len(people)):
        p = people[i]
        score = 0

        if "title" in person and "title" in p:
            if p["title"] == person["title"]:
                score += 1

        if "first" in person and "first" in p:
            if person["first"] == p["first"]:
                score += 1

        if "last" in person and "last" in p:
            if person["last"] == p["last"]:
                score += 1

        if "middle" in person and "middle" in p:
            for middle_initial in person["middle"]:
                if middle_initial in p["middle"]:
                    score += 1

        if "email" in person and "email" in p:
            if person["email"] == p["email"]:
                score += 1

        if score > 0:
            scores[i] = score

    return scores


def findOrganization(organizations, organization):
    """ Find and score an `organization` within `organizations`"""

    print "FIND[ORG](%s)" % organizationString(organization)

    scores = {}

    for i in range(0, len(organizations)):
        o = organizations[i]
        score = 0

        if "name" in organization and "name" in o:
            if organization["name"] == o["name"]:
                score += 1

        if "email" in organization and "email" in o:
            if organization["email"] == o["email"]:
                score += 1

        if "url" in organization and "url" in o:
            if organization["url"] == o["url"]:
                score += 1

        if score > 0:
            scores[i] = score

    return scores


def personString(person):
    """ Print a nice person string

        e.g. mr#bryce#d#mecum#mecum@nceas.ucsb.edu
    """

    person_strings = []

    if "title" in person:
        person_strings.append(person["title"])

    if "first" in person:
        person_strings.append(person["first"])

    if "middle" in person:
        person_strings.append(';'.join(person["middle"]))

    if "last" in person:
        person_strings.append(person["last"])

    if "email" in person:
        person_strings.append(person["email"])

    if "documents" in person:
        num_docs = len(person["documents"])

        person_strings.append("[%d]" % num_docs)

    return "#".join(person_strings)


def organizationString(organization):
    """ Print a nice organization string

        e.g ecotrends project#ecotrend@nmsu.edu#http://www.ecotrends.info#[23]
    """

    organization_strings = []

    if "name" in organization:
        organization_strings.append(organization["name"])

    if "email" in organization:
        organization_strings.append(organization["email"])

    if "url" in organization:
        organization_strings.append(organization["url"])

    if "documents" in organization:
        num_docs = len(organization["documents"])

        organization_strings.append("[%d]" % num_docs)

    return "#".join(organization_strings)


def main():
    people, organizations = processDirectory("results")

    print "All People:"
    print "----------"

    for person in people:
        print personString(person)

    print ""
    print "All Organizations:"
    print "----------"

    for organization in organizations:
        print organizationString(organization)
