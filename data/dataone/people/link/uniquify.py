""" uniquify.py

    Process the input file row-by-row, comparing the current row to rows
    seen previously. For people, if the current row has the same full name
    ('name') and email ('email') as a prevoiusly-seen record, don't save it.
    For organizations, if the current row has the same exact organnization name
    then don't save it.
"""

import unicodecsv
import json
import os.path
import sys


def uniquify(filename, type):
    """
        Prunes the file at `filename` according to the fixed rules present
        in either prunePeople or pruneOrganizations
    """

    input_file = open(filename, 'rb')
    output_file = open("%s_unique.csv" % type, 'wb')

    people_field_names = ['Id', 'name', 'organization', 'address', 'email',
                          'phone', 'document', 'type', 'format']

    organization_field_names = ['Id', 'name', 'address',
                                'email', 'phone', 'document', 'type', 'format']

    # Do the processing
    if type == "people":
        uniquifyPeople(input_file,
                       output_file,
                       people_field_names)
    else:
        uniquifyOrganizations(input_file,
                              output_file,
                              organization_field_names)

    # Close out both files
    input_file.close()
    output_file.close()


def uniquifyPeople(input_file, output_file, field_names):
    """
        Removes people with the same name and email.
    """

    input_reader = unicodecsv.DictReader(input_file,
                                         field_names)

    output_writer = unicodecsv.DictWriter(output_file,
                                          field_names)

    # Write headers
    output_writer.writerow(dict(zip(field_names,
                                    field_names)))

    # Skip header line
    input_reader.next()

    seen = {}

    # Remove identicals
    for row in input_reader:
        if len(row['name']) <= 0 or len(row['email']) <= 0:
            output_writer.writerow(row)
        else:
            key = row['name'] + row['email']

            if key in seen:
                print "%s same as %s" % (key.encode('utf-8'), row)
                seen[key].append(row)
            else:
                print "new"
                seen[key] = []
                seen[key].append(row)

                output_writer.writerow(row)

    with open("people_deduped.json", "wb") as f:
        f.write(json.dumps(seen,
                sort_keys=True,
                indent=2,
                separators=(',', ': ')))


def uniquifyOrganizations(input_file, output_file, field_names):
    """
        Removes organizations with the same exact name.
    """

    input_reader = unicodecsv.DictReader(input_file,
                                         field_names)

    output_writer = unicodecsv.DictWriter(output_file,
                                          field_names)

    # Write headers
    output_writer.writerow(dict(zip(field_names,
                                    field_names)))

    # Skip header line
    input_reader.next()

    seen = {}

    # Remove identicals
    for row in input_reader:
        if len(row['name']) <= 0:
            output_writer.writerow(row)
        else:
            key = row['name']

            if key in seen:
                print "%s same as %s" % (key.encode('utf-8'), row)
                seen[key].append(row)
            else:
                print "new"
                seen[key] = []
                seen[key].append(row)

                output_writer.writerow(row)

    with open("organizations_dedupe.json", "wb") as f:
        f.write(json.dumps(seen,
                sort_keys=True,
                indent=2,
                separators=(',', ': ')))


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

    uniquify(filename, filetype)
