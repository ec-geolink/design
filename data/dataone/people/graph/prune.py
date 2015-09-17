""" prune.py

    Remove people and organizations we definitely don't want to add to the
    graph.

    Takes in a CSV (input.csv)
    Creates a modified CSV (input_pruned.csv)
    Creats a log of what it rejected (pruned.csv)
"""

import unicodecsv
import re
import os.path
import sys


def prune(filename, type):
    """
        Prunes the file at `filename` according to the fixed rules present
        in either prunePeople or pruneOrganizations
    """

    input_file = open(filename, 'rb')
    retained_file = open("%s_pruned.csv" % type, 'wb')
    rejected_file = open("%s_pruned_rejected.csv" % type, 'wb')

    # Read in field names
    people_field_names = ["Id",
                           "full_name",
                           "salutation",
                           "first_name",
                           "middle_name",
                           "last_name",
                           "organization",
                           "address",
                           "address_delivery_point",
                           "address_city",
                           "address_postal",
                           "address_admin_area",
                           "address_country",
                           "email",
                           "phone",
                           "document",
                           "type",
                           "source",
                           "format"]

    organization_field_names = ["Id",
                                 "name",
                                 "address",
                                 "address_delivery_point",
                                 "address_city",
                                 "address_postal",
                                 "address_admin_area",
                                 "address_country",
                                 "email",
                                 "phone",
                                 "document",
                                 "type",
                                 "source",
                                 "format"]

    # Do the processing
    if type == "people":
        prunePeople(input_file,
                    retained_file,
                    rejected_file,
                    people_field_names)
    else:
        pruneOrganizations(input_file,
                           retained_file,
                           rejected_file,
                           organization_field_names)

    # Close out both files
    input_file.close()
    retained_file.close()
    rejected_file.close()


def prunePeople(input_file, retained_file, rejected_file, field_names):
    """
        Prunes the people in `input_file` and saves the cleaned up version
        in `output_file`
    """

    input_reader = unicodecsv.DictReader(input_file,
                                         field_names)

    retained_writer = unicodecsv.DictWriter(retained_file,
                                            field_names)

    rejected_writer = unicodecsv.DictWriter(rejected_file,
                                            field_names)

    # Write headers
    retained_writer.writerow(dict(zip(field_names,
                                      field_names)))
    rejected_writer.writerow(dict(zip(field_names,
                                      field_names)))

    # Skip header line
    input_reader.next()

    # Set up rules
    # TODO: Set up a regex for this?
    junk_names = ['test', 'read', 'test1', 'test 2', 'asdf', 'adfs',
                  'test test', 'tret trert', 'GAA', 'BBB', 'tetqe', 'GGGG',
                  'You and your mentor']

    patterns = {'wg': re.compile("NCEAS:?\s*\d+"),
                'justnumbers': re.compile("^\d*$"),
                'junknames': re.compile("^[a-z]{3,4}\s*\d*$"),
                'noletters': re.compile("^[^a-zA-Z\u0000-\u007F]+$"),
                'journal article': re.compile("\d+:\d+-\d+")}

    # TODO add pruning for
    # Journal of the Fisheries Research Board of Canada 33:2489-2499
    # Journal of Fish Biology 13:203-213

    # Prune
    for row in input_reader:
        # Should we prune the entire record?
        should_prune = False

        # Rule: Empty name
        if len(row['full_name']) <= 0:
            should_prune = True

        # Rule: Junk name
        if row['full_name'] in junk_names:
            should_prune = True

        # Don't prune unicode names
        try:
            bytes(row['full_name'])
        except UnicodeEncodeError:
            """
            Throwing this unicode error checks whether the string is unicode or
            not. I'm not sure how robust this method is but it works AFAIK
            """

            should_prune = False

        # Should we prune the address field only?
        # "Select state or territory here."

        if re.compile("Select state or territory here").search(row['address']):
            row['address'] = ''

        # Should we prune the organization field only?
        prune_organization = False

        for pattern in patterns:
            if patterns[pattern].search(row['organization']):
                # Prune organization unless it's Unicode
                prune_organization = True

                try:
                    bytes(row['organization'])
                except UnicodeEncodeError:
                    prune_organization = False

                if prune_organization is True:
                    row['organization'] = ''

        if should_prune is True:
            rejected_writer.writerow(row)
        else:
            retained_writer.writerow(row)


def pruneOrganizations(input_file, retained_file, rejected_file, field_names):
    """
        Prunes the organizations in `input_file` and saves the cleaned up
        version in `output_file`
    """

    input_reader = unicodecsv.DictReader(input_file,
                                         field_names)

    retained_writer = unicodecsv.DictWriter(retained_file,
                                            field_names)

    rejected_writer = unicodecsv.DictWriter(rejected_file,
                                            field_names)

    # Write headers
    retained_writer.writerow(dict(zip(field_names,
                                      field_names)))
    rejected_writer.writerow(dict(zip(field_names,
                                      field_names)))

    # Skip header line
    input_reader.next()

    # Set up rules
    junk_orgs = ["Select state or territory here.", "null", "test"]
    patterns = {'wg': re.compile("NCEAS:?\s*\d+"),
                'junk': re.compile("^[a-z]{3,4}\s*\d*$"),
                'justnumbers': re.compile("^\d+$"),
                'noletters': re.compile("^[^a-zA-Z]+$"),
                'journal article': re.compile("\d+:\d+-\d+")}

    # Prune
    for row in input_reader:
        should_prune = False

        # Rule: Empty name
        if len(row['name']) <= 0:
            should_prune = True

        for junk_org_name in junk_orgs:
            if junk_org_name == row['name']:
                should_prune = True

        for pattern in patterns:
            if patterns[pattern].search(row['name']):
                should_prune = True

        # Don't prune unicode names
        try:
            bytes(row['name'])
        except UnicodeEncodeError:
            """
            Throwing this unicode error checks whether the string is unicode or
            not. I'm not sure how robust this method is but it works AFAIK
            """

            should_prune = False

        if should_prune is True:
            rejected_writer.writerow(row)
        else:
            retained_writer.writerow(row)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Incorrect number of arguments. Please specifiy filename and " \
              "filetype."

        sys.exit()

    filename = sys.argv[1]
    filetype = sys.argv[2]

    if not os.path.isfile(filename):
        print "File at %s was not found. Exiting." % filename
        sys.exit()

    if filetype not in ["people", "organizations"]:
        print "Filetype was not one of [people, organizations]. Exiting."
        sys.exit()

    prune(filename, filetype)
