""" fgdc.py

    Processing functions for processing FGDC

    Spec: http://www.fgdc.gov/metadata/csdgm/00.html

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
                  <cntorg>Information Center for the Environment http://ice.ucdavis.edu</cntorg>
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
            <metstdn>FGDC Content Standard for Digital Geospatial Metadata</metstdn>
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
                    <cntorg>California Department of Public Health, CDPH</cntorg>
                    <cntper>Leah Godsey Walker, P.E. - Chief, Division of Drinking Water and Environmental Management</cntper>
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

    metadata/metainfo/metc  <cntinfo> cntorg + cntper + cntaddr + cntemail + cntvoice

    metadata/ptcontac       <cntinfo/cntperp> + cntper + cntaddr + cntvoice + cntemail
        For when the person is more important than the organization

    metadata/ptcontac       <cntinfo/cntorgp> + cntper + cntaddr + cntvoice + cntemail
        For when the organization is more important than the person


"""

import xml.etree.ElementTree as ET

def process(job, xmldoc, document):
    """
        Process XML document `xmldoc` with identifier `document` as if it
        is an EML document.
    """

    # TODO: Process ptcontac
    # TODO: Process others? org?

    info = xmldoc.find("./metainfo/metc/cntinfo")

    if info is not None:
        processContactInfo(job, info, document)


def processContactInfo(job, info, document):
    # Blank record
    record = {}

    # Branch here depending on whether we have cntorgp and/or cntperp
    # If it's a cntorgp, we save it as an organization
    # If it's a cntperp, we save it as a person

    cntperp = info.find("./cntperp")
    cntorgp = info.find("./cntorgp")

    if cntperp is not None:
        print "----"
        print "CNTPERP"
        print "----"
        name = cntperp.find("./cntper")
        org = cntperp.find("./cntorg")

        if name is not None:
            record['fgdc_name'] = name.text

        if org is not None:
            record['fgdc_org'] = org.text

    if cntorgp is not None:
        org = cntorgp.find("./cntorg")

        if org is not None:
            record['fgdc_org'] = org.text

    address = info.find("./cntaddr")
    email = info.find("./cntemail")
    voice = info.find("./cntvoice")

    if address is not None:
        fields = processAddress(address)
        for field in fields:
            record["fgdc_address_%s" % (field)] = fields[field]

    if email is not None and email.text is not None:
        record['fgdc_email'] = email.text

    if voice is not None and voice.text is not None:
        record['fgdc_voice'] = voice.text

    record['document'] = document

    print record

    if cntperp is not None:
        job.people.append(record)

    if cntorgp is not None:
        job.organizations.append(record)


def processAddress(address):
    address_node = address.find("./address")
    address_city = address.find("./city")
    address_state = address.find("./state")
    address_postal = address.find("./postal")
    address_country = address.find("./country")

    if any([address_node,
            address_city,
            address_state,
            address_postal,
            address_country]) is None:
            print "Invalid address, one was None"
            return

    address_fields = {
        'address': address_node.text,
        'city': address_city.text,
        'state': address_state.text,
        'postal': address_postal.text,
        'country': address_country.text
    }

    print address_fields

    return address_fields
