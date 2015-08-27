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

    people_field_names = ['Id', 'name', 'organization', 'address', 'email',
                          'phone', 'document', 'type', 'format']

    organization_field_names = ['Id', 'name', 'address',
                                'email', 'phone', 'document', 'type', 'format']

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

        Rules:
            - Empty name
            - Junk name ('test', 'read', etc)
            - Names with just numbers
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
                  'test test', 'tret trert', 'GAA', 'BBB', 'tetqe', 'GGGG']

    junk_regexes = {'justnumbers': re.compile("^\d*$"),
                    'junknames': re.compile("^[a-z]{3,4}\s*\d*$"),
                    'noletters': re.compile("^[^a-zA-Z\u0000-\u007F]+$")}

    # Prune
    for row in input_reader:
        should_prune = False

        # Rule: Empty name
        if len(row['name']) <= 0:
            should_prune = True

        # Rule: Junk name
        if row['name'] in junk_names:
            should_prune = True

        # Rule: Numbers
        if junk_regexes['justnumbers'].search(row['name']):
            should_prune = True

        if junk_regexes['junknames'].search(row['name']):
            should_prune = True

        if junk_regexes['noletters'].search(row['name']):
            should_prune = True

        if should_prune is True:
            print "Pruning: %s" % row
            rejected_writer.writerow(row)
        else:
            retained_writer.writerow(row)


def pruneOrganizations(input_file, retained_file, rejected_file, field_names):
    """
        Prunes the organizations in `input_file` and saves the cleaned up
        version in `output_file`

        Rules:
            - wg: Organization names like 'NCEAS: 12312 XYZ'. These are working
                groups and not organizations we want to store in GeoLink.
            - junk: Names like 'adf' and 'test 2'
            - justnumbers
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
    # patterns = {'wg': re.compile("NCEAS:? \d+\s*:.*")}
    patterns = {'wg': re.compile("NCEAS:?\s*\d+"),
                'junk': re.compile("^[a-z]{3,4}\s*\d*$"),
                'justnumbers': re.compile("^\d*$"),
                'noletters': re.compile("^[^a-zA-Z]+$")}

    # Prune
    for row in input_reader:
        should_prune = False

        # Rule: Empty name
        if len(row['name']) <= 0:
            should_prune = True

        # Rule: NCEAS working groups
        if patterns['wg'].search(row['name']):
            should_prune = True

        # Rule: Junk names
        if patterns['junk'].search(row['name']):
            should_prune = True

        # Rule Just numbers
        if patterns['justnumbers'].search(row['name']):
            should_prune = True

        if patterns['noletters'].search(row['name']):
            should_prune = True

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
