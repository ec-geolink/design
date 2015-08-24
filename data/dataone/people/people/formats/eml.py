""" eml.py

    Processing functions for processing EML

    The contents of the <creator> tags are extracted.
    <creator>s are formatted according to the eml-party module.

    EML eml-party Module:

    - creator
        - individualName [0:1] {required OR organizationName/positionName}
            - surName [1] {required}
            - givenName [0:n]
            - salutation [0:n]
        - organizationName [0:1] {required OR individualName/positionName}
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

    # Process individual or organization
    if individual is not None:  # Individual
        record = processIndividual(record, individual)

        # Add on org name is it exists
        if organization is not None:
            record['org'] = organization.text

    else:  # Organizaiton
        record['name'] = organization.text

    address = creator.find("./address")

    if address is not None:
        record = processAddress(record, address)

    email = creator.find("./electronicMailAddress")

    if email is not None:
        record['email'] = email.text

    phone = creator.find("./phone[@phonetype='voice']")

    if phone is not None:
        record['phone'] = phone.text

    record['document'] = document
    record['format'] = "EML"

    if individual is not None:
        job.people.append(record)
    else:
        job.organizations.append(record)


def processIndividual(record, individual):
    salutations = individual.findall("./salutation")
    given_names = individual.findall('./givenName')
    sur_name = individual.find('./surName')

    fields = []

    if salutations is not None:
        for salutation in salutations:
            fields.append(salutation.text)

    if given_names is not None:
        for given_name in given_names:
            fields.append(given_name.text)

    if sur_name is not None:
        fields.append(sur_name.text)

    if len(fields) > 0:
        record['name'] = " ".join([f for f in fields if f is not None])

    return record


def processAddress(record, address):
    delivery_points = address.findall("./deliveryPoint")
    city = address.find("./city")
    admin_area = address.find("./administrativeArea")
    postal = address.find("./postalCode")
    country = address.find("./country")

    fields = []

    if delivery_points is not None:
        for point in delivery_points:
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
