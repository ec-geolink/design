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

        self.people_columns = ["Id", "full_name", "salutation", "first_name",
                               "last_name", "organization", "address",
                               "address_delivery_point", "address_city",
                               "address_postal", "address_admin_area",
                               "address_country", "email", "phone", "document",
                               "type", "source", "format"]

        self.organization_columns = ["Id", "name", "address",
                                     "address_delivery_point", "address_city",
                                     "address_postal", "address_admin_area",
                                     "address_country", "email", "phone",
                                     "document", "type", "source", "format"]

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
