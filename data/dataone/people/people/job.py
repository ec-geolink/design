""" job.py
    Bryce Mecum (mecum@nceas.ucsb.edu)

    A Job processes a set of files in a directory for people and organization
    and exports a list of unique people and organizations and their respective
    documents.
"""

import processing
import helpers


class Job:
    def __init__(self, directory):
        self.people = []
        self.organizations = []
        self.directory = directory

    def run(self):
        processing.processDirectory(self)

    def summary(self):
        print "Job Summary\n----------"
        print "People: %d" % len(self.people)
        print "Organizations: %s" % len(self.organizations)

        if len(self.people) > 0:
            print "\nIndividuals\n----------"

        for person in self.people:
            print helpers.personString(person)

        if len(self.organizations) > 0:
            print "\nOrganizations\n----------"

        for organization in self.organizations:
            print helpers.organizationString(organization)
