""" find.py
    Bryce Mecum (mecum@nceas.ucsb.edu)

    Methods used for finding people and organizations.
"""

import helpers
import checks


def findPerson(job, person):
    """ Find and score a `person` within `people`"""

    print "FIND[PERSON](%s)" % helpers.personString(person)

    match = -1

    for i in range(0, len(job.people)):
        p = job.people[i]

        if checks.fieldsSame(person, p, ["email"]):
            print "Same email"
            match = i

        elif checks.fieldsSame(person, p, ["first", "last"]) and \
             checks.fieldsNotDifferent(person, p, ["email"]):
            print "Full name is not different but email is."
            match = i

    print "match is %d" % match

    return match


def findOrganization(job, organization):
    """ Find and score an `organization` within `organizations`"""

    print "FIND[ORG](%s)" % helpers.organizationString(organization)

    match = -1

    for i in range(0, len(job.organizations)):
        o = job.organizations[i]

        if checks.fieldsSame(organization, o, ["name"]):
            match = i

    return match
