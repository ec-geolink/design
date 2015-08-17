""" eml.py

    Processing functions for processing eml
"""

import re
from people import find


def process(job, xmldoc, document):
    """
        Process XML document `xmldoc` with identifier `document` as if it
        is an EML document.
    """

    # Process each <creator>
    creators = xmldoc.findall(".//creator")

    for creator in creators:
        processCreator(job,
                       creator,
                       document)


def processCreator(job, creator, document):
    """Process the <creator> tag in an EML document"""

    if creator.find("./individualName") is not None:
        person = processCreatorIndividual(job,
                                          creator,
                                          document)

        processPerson(job, person, document)

    elif creator.find("./organizationName") is not None:
        organization = processCreatorOrganization(job,
                                                  creator,
                                                  document)

        processOrganization(job, organization, document)


def processPerson(job, person, document):
    """ Processes a parsed EML creator that is an individual"""

    if not person:
        return

    match = find.findPerson(job, person)

    if match == -1:
        person["documents"] = [str(document)]

        job.people.append(person)
    else:
        existing = job.people[match]

        if "documents" in existing:
            existing["documents"].append(str(document))
        else:
            existing["documents"] = [str(document)]


def processOrganization(job, organization, document):
    """ Processes a parsed EML creator that is an organization"""

    if not organization:
        return

    match = find.findOrganization(job, organization)

    if match == -1:
        organization["documents"] = [str(document)]

        job.organizations.append(organization)
    else:
        existing = job.organizations[match]

        if "documents" in existing:
            existing["documents"].append(str(document))
        else:
            existing["documents"] = [str(document)]


def processCreatorIndividual(job, creator, document):
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

        person = processSalutation(person, salutation)
        person = processGivenName(person, given_name)
        person = processSurName(person, sur_name)

    user_id = creator.find("./userId")
    person = processUserId(person, user_id)

    email = creator.find("./electronicMailAddress")
    person = processEmail(person, email)

    return person


def processCreatorOrganization(job, creator, document):
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

    return organization


def processSalutation(person, salutation):
    """
    Adds information from the salutation to the current person.
    """

    if salutation is not None:
        title = salutation.text.lower()
        person["title"] = title.translate(None, ".")

    return person


def processGivenName(person, given_name):
    """
    Adds information from the given name to the current person.
    """

    if given_name is not None:
        first_name = given_name.text.lower()

        # First I.
        pattern_one = re.compile("\w+\s+\w{1}\.?")

        # First I. J.
        pattern_two = re.compile("\w+\s+\w{1}\.?\w{1}\.?")

        if pattern_one.match(first_name):
            first_name = first_name.split(" ")

            person["first"] = first_name[0]
        elif pattern_two.match(first_name):
            first_name = first_name.split(" ")

            person["first"] = first_name[0]
        else:
            person["first"] = first_name

    return person


def processSurName(person, sur_name):
    """
    Adds information from the sur name to the current person.
    """

    if sur_name is not None:
        person["last"] = sur_name.text.lower()

    return person


def processUserId(person, user_id):
    """
    Adds information from the user id to the current person.
    """

    if user_id is not None:
        user_id_fields = re.compile("(\w+=\w+)+").findall(user_id.text)

        if len(user_id_fields) > 0:
            fields = []

            for field in user_id_fields:
                k, v = field.split("=")

                if k and v:
                    fields.append({k.lower(): v.lower()})

            person["user_id"] = fields

    return person


def processEmail(person, email):
    """
    Adds information from the email to the current person.
    """

    if email is not None:
        person["email"] = email.text.lower()

    return person
