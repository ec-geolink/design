""" fgdc.py

    Processing functions for processing FGDC

    Spec: http://www.fgdc.gov/metadata/csdgm/00.html
    Relevant Section: http://www.fgdc.gov/metadata/csdgm/08.html

    Dataset creators are stored in the <origin> field.

    <idinfo>
        <citeinfo>
            <origin> <- Originator free text here

    "8.1 Originator -- the name of an organization or individual that
     developed the data set." So it's not possible to tell whether we are
     processing a person or an organization.

     Because there are no person/org metadata in this field, we lean on other
     sections of the file for information on the originator's metadata.


"""

import re


def process(xmldoc, document):
    """
        Process XML document `xmldoc` with identifier `document` as if it
        is an EML document.
    """

    records = []

    # Process non-originator info for metadata
    # DISABLED for now. I can't find any documents where this would be helpful.

    # info = xmldoc.find("./metainfo/metc/cntinfo")
    #
    # if info is not None:
    #     record = processContactInfo(info, document)
    #     records.append(record)


    # Process originator
    origin_nodes = xmldoc.findall("./idinfo/citation/citeinfo/origin")

    if origin_nodes is not None:
        for origin_node in origin_nodes:
            record = processOriginator(origin_node, document)
            records.append(record)

    # Copy in info the originator if there is a match
    #records = fillInOriginator(records) # DISABLED, see above.

    return records


def processOriginator(origin, document):
    """ Process the Originator (<origin>) element."""

    record = {}

    """ Decide of this is a person or an organization
        It looks like people are almost always in forms like:

            EHLERINGER, J.R.
            COOK, C.
            Brown, Sandra
            O'Neill, Elizabeth G.
    """

    # Make sure origin is a string of some sort
    if origin.text is None or len(origin.text) < 1:
        return record

    if re.search("[\w']+,\s+(\w+\.?\s?)+", origin.text):
        name_split = origin.text.split(",")

        record['first_name'] = name_split[1].strip()
        record['last_name'] = name_split[0].strip().capitalize() # LAST to Last
        record['full_name'] = " ".join([record['first_name'], record['last_name']])

        # Remove middle names inside given name
        name_parts = re.findall('(\w+)\s+([\w\.?\s?]+)', record['first_name'])

        if len(name_parts) == 1:
            # Prevent non-people names from being split up
            # i.e.[('Inventory', 'and Monitoring Program')]
            # Only do the following if the second string is short (<5 chars)

            if len(name_parts[0][1]) < 5:
                record['first_name'] = name_parts[0][0]
                record['middle_name'] = name_parts[0][1].replace(".", "")

        record['type'] = 'person'
    else:
        record['name'] = origin.text
        record['type'] = 'organization'

    record['document'] = document
    record['source'] = 'originator'
    record['format'] = 'FGDC'

    return record


def processContactInfo(info, document):
    # Blank record
    record = {}

    # Branch here depending on whether we have cntorgp and/or cntperp
    # If it's a cntorgp, we save it as an organization
    # If it's a cntperp, we save it as a person

    cntperp = info.find("./cntperp")
    cntorgp = info.find("./cntorgp")

    if cntperp is not None:
        name = cntperp.find("./cntper")
        org = cntperp.find("./cntorg")

        if name is not None and name.text is not None:
            record['name'] = name.text.strip()

        if org is not None and org.text is not None:
            record['organization'] = org.text.strip()

    if cntorgp is not None:
        org = cntorgp.find("./cntorg")

        if org is not None and org.text is not None:
            record['organization'] = org.text.strip()

    address = info.find("./cntaddr")
    email = info.find("./cntemail")
    voice = info.find("./cntvoice")

    if address is not None:
        processAddress(record, address)

    if email is not None and email.text is not None:
        record['email'] = email.text.strip().replace(" at ", "@")

    if voice is not None and voice.text is not None:
        record['phone'] = voice.text.strip()

    record['document'] = document
    record['format'] = 'FGDC'
    record['source'] = 'contact'

    if cntperp is not None:
        record['type'] = 'person'
    else:
        record['type'] = 'organization'

        if 'organization' in record:
            record['name'] = record['organization']  # Swap in org name

    return record


def processAddress(record, address):
    address_nodes = address.findall("./address")
    city = address.find("./city")
    state = address.find("./state")
    postal = address.find("./postal")
    country = address.find("./country")

    fields = []

    if address_nodes is not None:
        address_node_texts = []

        for node in address_nodes:
            if node.text is not None:
                fields.append(node.text.strip())
                address_node_texts.append(node.text.strip())

        if len(address_node_texts) > 0:
            record['address_delivery_point'] = " ".join(address_node_texts)

    if city is not None and city.text is not None:
        fields.append(city.text.strip())
        record['address_city'] = city.text.strip()

    if state is not None and state.text is not None:
        fields.append(state.text.strip())
        record['address_admin_area'] = state.text.strip()

    if postal is not None and postal.text is not None:
        fields.append(postal.text.strip())
        record['address_postal'] = postal.text.strip()

    if country is not None and country.text is not None:
        fields.append(country.text.strip())
        record['address_country'] = country.text.strip()

    if len(fields) > 0:
        record['address'] = " ".join([f for f in fields if f is not None])

    return record


def fillInOriginator(records):
    """ Use information from other records in this document to fill in
    information about the originator.

    Not run for now. See note above.
    """

    originator = None

    for record in records:
        if 'source' in record and record['source'] == 'originator':

            originator = record

    # Return early if we didn't find one
    if originator is None:
        return records

    for record in records:
        if 'source' not in record or record['source'] != 'originator':
            print "Fill in from other record"
            print record

            # if 'last_name' in record

    return records
