""" eml.py

    Processing functions for processing EML.

    The contents of the <creator> tags are extracted.
    <creator>s are formatted according to the eml-party module.

    EML eml-party Module:

    - creator
        - individualName [0:1] {required OR organizationName/positionName}
            - surName [1] {required}
            - givenName [0:n]
            - salutation [0:n]
        - organizationName [0:n] {required OR individualName/positionName}
        - positionName [0:1] {required OR individualName/organizationName}
        - address [0:n]
        - phone [0:n]
        - electronicMailAddress [0:n]
        - address [0:n]
            - deliveryPoint [0:n]
            - city [0:1]
            - administrativeArea [0:1]
            - postalCode [0:1]
            - country [0:1]
"""

# TODO: Check out whether this stuff changes over spec versions
# TODO: Check if the eml- subfiles need to be processed

import re


def process(xmldoc, document):
    """
        Process XML document `xmldoc` with identifier `document` as if it
        is an EML document.
    """

    # Process each <dataset/creator>
    creators = xmldoc.findall(".//dataset/creator")

    records = []

    for creator in creators:
        processed_creators = processCreator(creator, document)

        for processed_creator in processed_creators:
            records.append(processed_creator)

    return records


def processCreator(creator, document):
    """ Proccess a <creator> tag for an individual.
    """

    """ When a creator has multiple organizations, we duplicate their record
    once for each organization."""
    records = [] # Store all records parsed
    record = {} # Stores the primary record being parsed

    individual = creator.find("./individualName")
    organizations = creator.findall("./organizationName")

    # Process individual or organization
    if individual is not None:  # Individual
        record = processIndividual(record, individual)
    elif organizations is not None:  # Organizaiton
        org_strings = []

        for organization in organizations:
            org_text = organization.text

            if org_text is not None:
                org_strings.append(org_text.strip())

        if len(org_strings) > 0:
            record['name'] = " ".join([o for o in org_strings if o is not None and len(o) > 0])

    address = creator.find("./address")

    if address is not None:
        record = processAddress(record, address)

    email = creator.find("./electronicMailAddress")

    if email is not None and email.text is not None:
        record['email'] = email.text.strip().replace(" at ", "@")

    phone = creator.find("./phone[@phonetype='voice']")

    if phone is not None and phone.text is not None:
        record['phone'] = phone.text.strip()

    record['document'] = document
    record['format'] = "EML"

    """
    Only attribute 'creator' to this record if it doesn't have an id attrib.

        e.g. <creator> versus <creator id="site">
    """

    if 'id' not in creator.attrib:
        record['source'] = 'creator'
    else:
        record['source'] = 'other'

    if individual is not None:
        record['type'] = 'person'

        # for organization in organizations:
        #     if organization.text is not None:
        #         org_text = organization.text.strip()
        #
        #         new_record = record.copy()
        #         new_record['type'] = 'organization'
        #         new_record['organization'] = org_text
        #         records.append(new_record)
    else:
        record['type'] = 'organization'

    # Append primary record to records list
    records.append(record)

    return records


def processIndividual(record, individual):
    salutations = individual.findall("./salutation")
    given_names = individual.findall('./givenName')
    sur_name = individual.find('./surName')

    fields = []

    if salutations is not None:
        all_salutations = []

        for salutation in salutations:
            if salutation.text is not None:
                fields.append(salutation.text.strip())
                all_salutations.append(salutation.text.strip())

        if len(all_salutations) > 0:
            record['salutation'] = " ".join(all_salutations).replace(".", "")

    if given_names is not None:
        all_given_names = []

        for given_name in given_names:
            if given_name.text is not None:
                fields.append(given_name.text.strip())
                all_given_names.append(given_name.text.strip())

        if len(all_given_names) > 0:
            record['first_name'] = " ".join(all_given_names)

            # Remove middle names inside given name
            name_parts = re.findall('(\w+)\s+([\w\.?\s?]+)', record['first_name'])

            if len(name_parts) == 1:
                record['first_name'] = name_parts[0][0]
                record['middle_name'] = name_parts[0][1].replace(".", "")



    if sur_name is not None and sur_name.text is not None:
        fields.append(sur_name.text.strip())
        record['last_name'] = sur_name.text.strip()

    if len(fields) > 0:
        record['full_name'] = " ".join([f for f in fields if f is not None])

    return record


def processAddress(record, address):
    delivery_points = address.findall("./deliveryPoint")
    city = address.find("./city")
    admin_area = address.find("./administrativeArea")
    postal = address.find("./postalCode")
    country = address.find("./country")

    fields = []

    if delivery_points is not None:
        delivery_point_nodes = []

        for point in delivery_points:
            if point.text is not None:
                fields.append(point.text.strip())
                delivery_point_nodes.append(point.text.strip())

        if len(delivery_point_nodes) > 0:
            record['address_delivery_point'] = " ".join(delivery_point_nodes)

    if city is not None and city.text is not None:
        fields.append(city.text.strip())
        record['address_city'] = city.text.strip()

    if admin_area is not None and admin_area.text is not None:
        fields.append(admin_area.text.strip())
        record['address_admin_area'] = admin_area.text.strip()

    if postal is not None and postal.text is not None:
        fields.append(postal.text.strip())
        record['address_postal'] = postal.text.strip()

    if country is not None and country.text is not None:
        fields.append(country.text.strip())
        record['address_country'] = country.text.strip()

    if len(fields) > 0:
        record['address'] = " ".join([f for f in fields if f is not None])

    return record
