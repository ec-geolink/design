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
import uuid


def uniquify(filename, type):
    """
        Prunes the file at `filename` according to the fixed rules present
        in either prunePeople or pruneOrganizations
    """

    input_file = open(filename, 'rb')
    output_file = open("%s_unique.csv" % type, 'wb')

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
                           "format",
                           "uri"]

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
                                 "format",
                                 "uri"]

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

    field_names.append("same")
    output_writer = unicodecsv.DictWriter(output_file,
                                          field_names)

    # Write headers
    output_writer.writerow(dict(zip(field_names,
                                    field_names)))

    # Skip header line
    input_reader.next()

    seen = {}
    unmatched = []

    # Remove identicals
    for row in input_reader:
        key = None # Default

        # Override default key if we have a usable one
        if len(row['last_name']) > 0 and len(row['email']) > 0:
            key = row['last_name'] + "#" + row['email']
            key = key.encode('utf-8')

        if key is None:
            unmatched.append({'records': row, 'uri': str(uuid.uuid4())})
        else:
            if key in seen:
                row['same'] = key
                seen[key]['records'].append(row)
            else:
                seen[key] = {}

                if 'records' not in seen[key]:
                    seen[key]['records'] = []

                if 'uri' not in seen[key]:
                    seen[key]['uri'] = str(uuid.uuid4())

                seen[key]['records'].append(row)

        output_writer.writerow(row)

    num_unique = len(seen) + len(unmatched)
    print "Unique people: %d" % num_unique

    # Add in unmatched records to seen dict
    seen['unmatched'] = unmatched

    with open("people_unique.json", "wb") as f:
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

    field_names.append("same")
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
        if len(row['name']) > 0:
            key = row['name']
            key = key.encode('utf-8')

            if key in seen:
                row['same'] = key
                row['uri'] = str(uuid.uuid4())
                seen[key]['records'].append(row)
            else:
                seen[key] = { 'records': [ row ], 'uri': str(uuid.uuid4())}

        output_writer.writerow(row)

    num_unique = len(seen)
    print "Unique organizations: %d" % num_unique

    with open("organizations_unique.json", "wb") as f:
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
