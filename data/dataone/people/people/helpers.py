""" helpers.py
    Bryce Mecum (mecum@nceas.ucsb.edu)

    Helpful methods used for the rest of the package.
"""


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
