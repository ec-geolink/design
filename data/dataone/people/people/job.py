""" job.py
    Bryce Mecum (mecum@nceas.ucsb.edu)

    A Job processes a set of files in a directory for people and organization
    and exports a list of unique people and organizations and their respective
    documents.
"""

import processing
import helpers
import unicodecsv


class Job:
    def __init__(self, directory):
        self.people = []
        self.organizations = []
        self.directory = directory
        self.people_file = "people_dump.csv"
        self.organizations_file = "organizations_dump.csv"

        self.people_columns = ["Id", "name", "organization", "address", "email", "phone", "document", "type", "format"]
        self.organization_columns = ["Id", "name", "address", "email", "phone", "document", "type", "format"]

        self.people_row_id = 0
        self.organization_row_id = 0

        # Open file handles
        self.people_file_handle = open(self.people_file, "wb")
        self.organizations_file_handle = open(self.organizations_file, "wb")

        # Create writers
        self.people_writer = unicodecsv.writer(self.people_file_handle, encoding='utf-8')
        self.organization_writer = unicodecsv.writer(self.organizations_file_handle, encoding='utf-8')

        # Write header columns
        self.people_writer.writerow(self.people_columns)
        self.organization_writer.writerow(self.organization_columns)

    def run(self):
        processing.processDirectory(self)

    def finish(self):
        if self.people_file_handle:
            self.people_file_handle.close()

        if self.organizations_file_handle:
            self.organizations_file_handle.close()

    def writePerson(self, record):
        if record is None:
            return

        record["Id"] = self.people_row_id

        row = []
        for colname in self.people_columns:
            if colname in record:
                row.append(record[colname])
            else:
                row.append("")

        self.people_writer.writerow(row)
        self.people_row_id += 1

    def writeOrganization(self, record):
        if record is None:
            return

        record["Id"] = self.organization_row_id

        row = []
        for colname in self.organization_columns:
            if colname in record:
                row.append(record[colname])
            else:
                row.append("")

        self.organization_writer.writerow(row)
        self.organization_row_id += 1

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
