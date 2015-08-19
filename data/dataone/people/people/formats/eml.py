""" eml.py

    Processing functions for processing eml
"""

# TODO: Get more fields from EML spec, like address
# TODO: Check out whether this stuff changes over spec versions
# TODO: Check if the eml- subfiles need to be processed


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
        record['eml_org'] = organization.text

    address = creator.find("./address")

    if address is not None:
        record = processAddress(record, address)

    user_id = creator.find("./userId")

    if user_id is not None:
        record['eml_user_id'] = user_id.text

    email = creator.find("./electronicMailAddress")

    if email is not None:
        record['eml_email'] = email.text

    phone = creator.find("./phone[@phonetype='voice']")

    if phone is not None:
        record['eml_phone'] = phone.text

    record['document'] = document
    
    if individual is None:
        job.organizations.append(record)
    else:
        job.people.append(record)


def processIndividual(record, individual):
    salutation = individual.find("./salutation")
    sur_name = individual.find('./surName')
    given_name = individual.find('./givenName')

    if salutation is not None:
        record["eml_title"] = salutation.text

    if given_name is not None:
        record["eml_last"] = given_name.text

    if sur_name is not None:
        record["eml_first"] = sur_name.text

    return record


def processAddress(record, address):
    delivery_point = address.find("./deliveryPoint")
    city = address.find("./city")
    admin_area = address.find("./administrativeArea")
    postal = address.find("./postalCode")

    if delivery_point is not None:
        record['eml_delivery_point'] = delivery_point.text

    if city is not None:
        record['eml_city'] = city.text

    if admin_area is not None:
        record['eml_admin_area'] = admin_area.text

    if postal is not None:
        record['eml_postal'] = postal.text

    return record
