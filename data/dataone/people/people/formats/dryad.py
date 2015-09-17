""" dryad.py

    Processing functions for processing Dryad metadata

    TODO: Handle the XML entities Jonnson and stuff. See Dryad.
"""

import re
from people import find


def process(xmldoc, document):
    """
        Process XML document `xmldoc` with identifier `document` as if it
        is an EML document.
    """

    # Process each <creator>
    creators = xmldoc.findall(".//ns2:creator", { 'ns2': 'http://purl.org/dc/terms/'})

    records = []

    for creator in creators:
        if creator.text is None:
            continue

        record = {}
        name = creator.text.strip()

        name_parts = name.split(",")

        # Check if "Last, First" is plausible
        if len(name_parts) == 2:
            record['first_name'] = name_parts[1].strip()
            record['last_name'] = name_parts[0].strip()
            record['full_name'] = ' '.join([name_parts[1].strip(), name_parts[0].strip()])

            # Remove middle names inside given name
            first_name_parts = re.findall('(\w+)\s+([\w\.?\s?]+)', record['first_name'])

            if len(first_name_parts) == 1:
                record['first_name'] = first_name_parts[0][0]
                record['middle_name'] = first_name_parts[0][1].replace(".", "")

        else:
            record['full_name'] = name

        record['format'] = "Dryad"
        record['source'] = "creator"
        record['type'] = 'person'
        record['document'] = document

        records.append(record)

    return records
