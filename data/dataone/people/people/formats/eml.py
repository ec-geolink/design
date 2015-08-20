""" eml.py

    Processing functions for processing eml
"""

# TODO: Get more fields from EML spec, like address
# TODO: Check out whether this stuff changes over spec versions
# TODO: Check if the eml- subfiles need to be processed
# TODO: Add <associatedParty>
# TODO: Add <positionName>

import re
from people import find


def process(job, xmldoc, document):
    """
        Process XML document `xmldoc` with identifier `document` as if it
        is an EML document.
    """

    # Process each <creator>
    creators = xmldoc.findall(".//creator")

    for creator in creators:
        processCreator(job,
                       creator,
                       document)


def processCreator(job, creator, document):
    """ Proccess a <creator> tag for an individual.
    """

    record = {}

    individual = creator.find("./individualName")
    organization = creator.find("./organizationName")

    if individual is not None:
        record = processIndividual(record, individual)

    if organization is not None:
        record['org'] = organization.text

    address = creator.find("./address")

    if address is not None:
        record = processAddress(record, address)

    user_id = creator.find("./userId")

    if user_id is not None:
        record['eml_user_id'] = user_id.text

    email = creator.find("./electronicMailAddress")

    if email is not None:
        record['email'] = email.text

    phone = creator.find("./phone[@phonetype='voice']")

    if phone is not None:
        record['phone'] = phone.text

    record['document'] = document
    record['format'] = "EML"

    if individual is None:
        job.organizations.append(record)
    else:
        job.people.append(record)


def processIndividual(record, individual):
    salutation = individual.find("./salutation")
    sur_name = individual.find('./surName')
    given_name = individual.find('./givenName')

    fields = []

    if salutation is not None:
        fields.append(salutation.text)

    if given_name is not None:
        fields.append(given_name.text)

    if sur_name is not None:
        fields.append(sur_name.text)

    if len(fields) > 0:
        record['name'] = " ".join([f for f in fields if f is not None])

    return record


def processAddress(record, address):
    delivery_point = address.findall("./deliveryPoint")
    city = address.find("./city")
    admin_area = address.find("./administrativeArea")
    postal = address.find("./postalCode")
    country = address.find("./country")

    fields = []

    # There can be multiple <deliveryPoint)
    if delivery_point is not None:
        for point in delivery_point:
            print "deliveryPoint is %s" % point.text
            fields.append(point.text)

    if city is not None:
        fields.append(city.text)

    if admin_area is not None:
        fields.append(admin_area.text)

    if postal is not None:
        fields.append(postal.text)

    if country is not None:
        fields.append(country.text)

    if len(fields) > 0:
        record['address'] = " ".join([f for f in fields if f is not None])

    return record
