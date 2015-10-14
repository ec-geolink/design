""" helpers.py
    Bryce Mecum (mecum@nceas.ucsb.edu)

    Helpful methods used for the rest of the package.
"""


def personString(person):
    """ Print a nice person string

        e.g. mr#bryce#d#mecum#mecum@nceas.ucsb.edu
    """

    person_strings = []

    for field in person:
        person_strings.append("%s:%s" % (field, person[field]))

    return "#".join(person_strings)


def organizationString(organization):
    """ Print a nice organization string

        e.g ecotrends project#ecotrend@nmsu.edu#http://www.ecotrends.info#[23]
    """

    organization_strings = []

    for field in organization:
        organization_strings.append("%s:%s" % (field, organization[field]))

    return "#".join(organization_strings)
