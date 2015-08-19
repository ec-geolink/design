""" dryad.py

    Processing functions for processing Dryad metadata
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
        record = {'dryad_name': creator.text}
        job.people.append(record)
