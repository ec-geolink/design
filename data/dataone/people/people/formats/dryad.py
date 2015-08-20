""" dryad.py

    Processing functions for processing Dryad metadata

    TODO: Handle the XML entities Jonnson and stuff. See Dryad.
"""

import re
from people import find


def process(job, xmldoc, document):
    """
        Process XML document `xmldoc` with identifier `document` as if it
        is an EML document.
    """

    # Process each <creator>
    creators = xmldoc.findall(".//ns2:creator", { 'ns2': 'http://purl.org/dc/terms/'})

    for creator in creators:
        record = {'name': creator.text}
        record['format'] = "Dryad"
        job.people.append(record)
