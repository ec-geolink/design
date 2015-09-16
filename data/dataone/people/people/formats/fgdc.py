""" fgdc.py

    Processing functions for processing FGDC

    Spec: http://www.fgdc.gov/metadata/csdgm/00.html
    Relevant Section: http://www.fgdc.gov/metadata/csdgm/08.html

    Dataset creators are stored in the <origin> field.

    <idinfo>
        <citeinfo>
            <origin> <- Originator free text here

    People and organization information comes in two locations in the document.

    Location 1: /metadata/metainfo/metc
    This is the "metadata contact"

    <metadata>
        ...
        <metainfo>
            <metd>20120328</metd>
            <metrd/>
            <metfrd/>
            <metc>
              <cntinfo>
                <cntorgp>
                  <cntorg>Information Center for the Environment...</cntorg>
                  <cntper>Rob Coman</cntper>
                </cntorgp>
                <cntpos/>
                <cntaddr>
                  <addrtype>mailing</addrtype>
                  <address>University of California, Davis</address>
                  <address>One Shields Avenue</address>
                  <city>Davis</city>
                  <state>CA</state>
                  <postal>95616</postal>
                  <country>USA</country>
                </cntaddr>
                <cntvoice/>
                <cntemail/>
              </cntinfo>
            </metc>
            <metstdn>
                FGDC Content Standard for Digital Geospatial Metadata
            </metstdn>
            <metstdv>FGDC-STD-001-1998</metstdv>
            </metainfo>
        </metadata>

    Location 2: /metadata/ptcontac
    This seems to be the contact for the data itself.

    <metadata>
        ...
        <ptcontac>
            <cntinfo>
                <cntorgp>
                    <cntorg>California Department of P...</cntorg>
                    <cntper>Leah Godsey Walker, P.E. - Chief, D...</cntper>
                </cntorgp>
                <cntaddr>
                    <addrtype>mailing</addrtype>
                    <address>1615 Capitol Avenue</address>
                    <city>Sacramento</city>
                    <state>CA</state>
                    <postal>95815-5015</postal>
                    <country>USA</country>
                </cntaddr>
                <cntvoice/>
                <cntemail/>
            </cntinfo>
        </ptcontac>
    </metadata>

    Fields to extract:

    metadata/metainfo/metc  <cntinfo> cntorg + cntper + cntaddr +
                                                cntemail + cntvoice

    metadata/ptcontac       <cntinfo/cntperp> + cntper + cntaddr +
                                                cntvoice + cntemail
        For when the person is more important than the organization

    metadata/ptcontac       <cntinfo/cntorgp> + cntper + cntaddr +
                                                cntvoice + cntemail
        For when the organization is more important than the person
"""

import re


def process(job, xmldoc, document):
    """
        Process XML document `xmldoc` with identifier `document` as if it
        is an EML document.
    """

    # TODO: Process ptcontac
    # TODO: Process others? org?

    # info = xmldoc.find("./metainfo/metc/cntinfo")
    print "FGDC document being processed."
    origin_nodes = xmldoc.findall("./idinfo/citation/citeinfo/origin")
    print "Found %d origin nodes." % len(origin_nodes)

    records = []

    # if info is not None:
    #     record = processContactInfo(job, info, document)
    #     records.append(record)

    if origin_nodes is not None:
        for origin_node in origin_nodes:
            record = processCreator(job, origin_node, document)
            records.append(record)

    return records


def processCreator(job, origin, document):
    """ Process the Originator (<origin>) element.
    """
    record = {}

    """ Decide of this is a person or an organization
        It looks like people are almost always in forms like:

            EHLERINGER, J.R.
            COOK, C.
            Brown, Sandra
            O'Neill, Elizabeth G.
    """
    print origin.text
    
    if re.search("[\w']+,\s+(\w+\.?\s?)+", origin.text):
        name_split = origin.text.split(",")

        record['first_name'] = name_split[1].strip()

        # Remove middle names inside given name
        name_parts = re.findall('(\w+)\s+([\w\.?\s?]+)', record['first_name'])
    
        if len(name_parts) == 1:
            # Prevent non-people names from being split up
            # i.e.[('Inventory', 'and Monitoring Program')]
            # Only do the following if the second string is short (<5 chars)

            print name_parts

            if len(name_parts[0][1]) < 5:
                print "fgdc name parts %s" % name_parts
                record['first_name'] = name_parts[0][0]
                record['middle_name'] = name_parts[0][1].replace(".", "")


        record['last_name'] = name_split[0].strip().capitalize() # LAST to Last
        record['full_name'] = " ".join([record['first_name'], record['last_name']])

        record['type'] = 'person'
    else:
        record['name'] = origin.text
        record['type'] = 'organization'

    record['source'] = 'creator'
    record['format'] = 'FGDC'

    return record


def processContactInfo(job, info, document):
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
        record['email'] = email.text.strip()

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
