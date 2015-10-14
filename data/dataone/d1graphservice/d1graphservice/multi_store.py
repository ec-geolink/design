"""
multi_store.py

A class to store interface with a set of triple stores. This is used when
triple stores need to be kept separate so each store can easily be exported
to separate RDF/XML or TTL files.
"""

import urllib
import uuid

from d1graphservice import util


class MultiStore():
    def __init__(self, stores, namespaces):
        """
        Handles storage and dispatch to multiple stores.

        Arguments:
            stores: Dict
                Keys should be strings
                Values should be of instance of class Store
        """

        if stores is None:
            raise Exception("No stores provided.")

        self.stores = stores
        self.ns = namespaces


    def load(self):
        """
        Load triples into the stores from files.
        """


    def save(self):
        """
        Save triples from each store into separate files.
        """

        for store_name in self.stores:
            store = self.stores[store_name]
            store.export("%s-testing.ttl" % store_name)


    def ns_interp(self, text):
        """
        Helper function to call util.ns_interp without having to specify
        namespaces.

        Arguments:
            text: str
                The text to interpolate, i.e., 'example:foo'
        """

        return util.ns_interp(text, self.ns)


    def findPerson(self, family, email):
        """
        Finds a person by their family name and email.
        """

        if 'people' not in self.stores:
            raise Exception("Person store not found.")

        store = self.stores['people']

        condition = {
            'glview:nameFamily': family,
            'foaf:mbox': "<mailto:%s>" % email
        }

        find_result = store.find(condition)

        if len(find_result) < 1:
            print "empty find result"
            return None

        return find_result[0]['subject']['value']


    def personExists(self, family, email):
        """
        Returns True or False whether the person with the given family name
        and email exists (has a URI).
        """

        result = self.findPerson(family, email)

        if result is None or len(result) < 1:
            return False
        else:
            return True


    def findOrganization(self, name):
        """
        Finds an organization by their name.
        """

        if 'organizations' not in self.stores:
            raise Exception("Organization store not found.")

        store = self.stores['organizations']

        condition = {
            'rdfs:label': name,
        }

        find_result = store.find(condition)

        if len(find_result) < 1:
            return None

        return find_result[0]['subject']['value']


    def organizationExists(self, name):
        """
        Returns True or False whether the organization with the given name
        exists (has a URI).
        """

        result = self.findOrganization(name)

        if result is None or len(result) < 1:
            return False
        else:
            return True


    def addPerson(self, record):
        key = self.get_key(record)

        if key is None:
            person_uri = self.mintURI('d1people')
        else:
            last,email = key.split("#")

            if self.personExists(last, email):
                person_uri = "<%s>" % self.findPerson(last, email)
                print "%s already existed. Using existing URI of %s." % (key, person_uri)

            else:
                person_uri = self.mintURI('d1people')

        self.addPersonTriples(person_uri, record)


    def addOrganization(self, record):
        key = self.get_key(record)

        if key is None:
            organization_uri = self.mintURI('d1org')
        else:
            if self.organizationExists(key):
                organization_uri = "<%s>" % self.findOrganization(key)
                print "%s already existed. Using existing URI of %s." % (key, organization_uri)
            else:
                print "  notexist"
                organization_uri = self.mintURI('d1org')

        self.addOrganizationTriples(organization_uri, record)


    def addDataset(self, doc, scimeta, formats = {}):
        """
        This method needs to determine if the dataset is already in the graph.
        This means that there may be triples in in datasets, people, and
        organizations that need to be deleted.

        Parameters:

            doc:
                XML from the <doc> tag off the Solr index
        """

        identifier = doc.find(".//str[@name='identifier']").text

        print "addDataset"

        if any(['d1resolve:'+urllib.quote_plus(identifier), '?p', '?o']):
            self.deleteDatasetTriples(doc, scimeta, formats)

        # self.addDatasetTriples(doc, scimeta, formats)


    def addDatasetTriples(self, doc, scimeta, formats = {}):
        """

        TODO:
            submitter
            rightsholder
            funding
            measurementType
        """

        if 'datasets' not in self.stores:
            raise Exception("Datasets store not found.")

        store = self.stores['datasets']


        identifier = doc.find(".//str[@name='identifier']").text
        identifier_esc = urllib.quote_plus(identifier)

        # type Dataset
        store.add(['d1resolve:'+identifier_esc, 'rdf:type', 'glview:Dataset'])

        # Title
        title_element = doc.find("./str[@name='title']")

        if title_element is not None:
            store.add(['d1resolve:'+identifier_esc, 'glview:title', title_element.text])
            store.add(['d1resolve:'+identifier_esc, 'rdfs:label', title_element.text])

        # Add glview Identifier
        id_blank_node = "<_:%s#identifier>" % identifier

        # Determine identifier scheme
        if (identifier.startswith("doi:") |
                identifier.startswith("http://doi.org/") | identifier.startswith("https://doi.org/") |
                identifier.startswith("https://dx.doi.org/") | identifier.startswith("https://dx.doi.org/")):
            scheme = 'doi'
        elif (identifier.startswith("ark:")):
            scheme = 'ark'
        elif (identifier.startswith("http:")):
            scheme = 'uri'
        elif (identifier.startswith("https:")):
            scheme = 'uri'
        elif (identifier.startswith("urn:")):
            scheme = 'urn'
        else:
            scheme = 'local-resource-identifier-scheme'

        store.add([id_blank_node, 'rdf:type', 'glview:Identifier'])
        store.add([id_blank_node, 'glview:hasIdentifierValue', identifier])
        store.add([id_blank_node, 'rdfs:label', identifier])
        store.add([id_blank_node, 'glview:hasIdentifierScheme', 'datacite:'+scheme])
        store.add(['d1resolve:'+identifier_esc, 'glview:hasIdentifier', id_blank_node])

        # Abstract
        abstract_element = doc.find("./str[@name='abstract']")

        if (abstract_element is not None):
            store.add(['d1resolve:'+identifier_esc, 'glview:description', abstract_element.text])

        # Spatial Coverage
        bound_north = doc.find("./float[@name='northBoundCoord']")
        bound_east = doc.find("./float[@name='eastBoundCoord']")
        bound_south = doc.find("./float[@name='southBoundCoord']")
        bound_west = doc.find("./float[@name='westBoundCoord']")

        if all(ele is not None for ele in [bound_north, bound_east, bound_south, bound_west]):
            if bound_north.text == bound_south.text and bound_west.text == bound_east.text:
                wktliteral = "POINT (%s %s)" % (bound_north.text, bound_east.text)
            else:
                wktliteral = "POLYGON ((%s %s, %s %s, %s %s, %s, %s))" % (bound_west.text, bound_north.text, bound_east.text, bound_north.text, bound_east.text, bound_south.text, bound_west.text, bound_south.text)

            store.add(['d1resolve:'+identifier_esc, 'glview:hasGeometryAsWktLiteral', wktliteral])

        # Temporal Coverage
        start_date = doc.find("./date[@name='startDate']")
        end_date = doc.find("./date[@name='endDate']")

        if start_date is not None:
            store.add(['d1resolve:'+identifier_esc, 'glview:hasStartDate', start_date.text])

        if end_date is not None:
            store.add(['d1resolve:'+identifier_esc, 'glview:hasEndDate', end_date.text])

        # Repositories: authoritative, replica, origin
        # Authoritative MN
        repository_authMN = doc.find("./str[@name='authoritativeMN']")
        store.add(['d1resolve:'+identifier_esc, 'glview:hasAuthoritativeDigitalRepository', 'd1repo:'+repository_authMN.text])

        # Replica MN's
        repository_replicas = doc.findall("./arr[@name='replicaMN']/str")

        for repo in repository_replicas:
            store.add(['d1resolve:'+identifier_esc, 'glview:hasReplicaDigitalRepository', 'd1repo:'+repository_authMN.text])

        # Origin MN
        repository_datasource = doc.find("./str[@name='datasource']")
        store.add(['d1resolve:'+identifier_esc, 'glview:hasOriginDigitalRepository', 'd1repo:'+repository_datasource.text])

        # Obsoletes as PROV#wasRevisionOf
        obsoletes_node = doc.find("./str[@name='obsoletes']")

        if obsoletes_node is not None:
            store.add(['d1resolve:'+identifier_esc, 'prov:wasRevisionOf', 'd1resolve:'+obsoletes_node.text])

        # Landing page
        store.add(['d1resolve:'+identifier_esc, 'glview:hasLandingPage', 'd1landing:'+identifier_esc])

        # Digital Objects
        digital_objects = doc.findall("./arr[@name='documents']/str")

        for digital_object in digital_objects:
            self.addDigitalObject(identifier, digital_object, formats)


    def addDigitalObject(self, identifier, digital_object, formats):
        """
        This is a wrapper function around addDigitalObjectTriples so digital
        objects can be removed when parent dataset is removed.
        """

        # TODO: Delete if necessary

        self.addDigitalObjectTriples(identifier, digital_object, formats)


    def addDigitalObjectTriples(self, identifier, digital_object, formats):
        """
        Notes:
            Creates only two triples (type and isPartOf) if the scimeta for the
            digital object can't be retrieved off the CN.
        """

        if 'datasets' not in self.stores:
            raise Exception("Datasets store not found.")

        store = self.stores['datasets']


        data_id = digital_object.text
        data_id_esc = urllib.quote_plus(data_id)

        store.add(['d1resolve:'+data_id_esc, 'rdf:type', 'glview:DigitalObject'])
        store.add(['d1resolve:'+data_id_esc, 'glview:isPartOf', 'd1resolve:'+urllib.quote_plus(identifier)])

        # Get data object meta
        data_meta = util.getXML("https://cn.dataone.org/cn/v1/meta/" + data_id_esc)

        if data_meta is None:
            print "Metadata for data object %s was not found. Continuing to next data object." % data_id
            return

        # Checksum and checksum algorithm
        checksum_node = data_meta.find(".//checksum")

        if checksum_node is not None:
            store.add(['d1resolve:'+data_id_esc, 'glview:hasChecksum', checksum_node.text])
            store.add(['d1resolve:'+data_id_esc, 'glview:hasChecksumAlgorithm', checksum_node.get("algorithm")])

        # Size
        size_node = data_meta.find("./size")

        if size_node is not None:
            store.add(['d1resolve:'+data_id_esc, 'glview:hasByteLength', size_node.text])

        # Format
        format_id_node = data_meta.find("./formatId")

        if format_id_node is not None:
            if format_id_node.text in formats:
                store.add(['d1resolve:'+data_id_esc, 'glview:hasFormat', formats[format_id_node.text]['uri']])

            else:
                print "Format not found."


        # Date uploaded
        date_uploaded_node = data_meta.find("./dateUploaded")

        if date_uploaded_node is not None:
            store.add(['d1resolve:'+data_id_esc, 'glview:dateUploaded', date_uploaded_node.text])


        # Submitter and rights holders
        # submitter_node = data_meta.find("./submitter")
        #
        # if submitter_node is not None:
        #     submitter_node_text = " ".join(re.findall(r"o=(\w+)", submitter_node.text, re.IGNORECASE))
        #
        #     if len(submitter_node_text) > 0:
        #         store.add(['d1resolve:'+data_id, 'glview:hasCreator', ])


        # rights_holder_node = data_meta.find("./rightsHolder")
        #
        # if rights_holder_node is not None:
        #     rights_holder_node_text = " ".join(re.findall(r"o=(\w+)", rights_holder_node.text, re.IGNORECASE))
        #
        #     if len(rights_holder_node_text) > 0:
        #         addStatement(model, d1resolve+data_id, ns["glbase"]+"hasRightsHolder", RDF.Uri("urn:node:" + rights_holder_node_text.upper()))


    def deleteDatasetTriples(self, doc, scimeta, formats):
        """
        This method will get called from addDataset() if the dataset already
        exists in the graph.

        In deleting a dataset's triples, we'll also need modify triples in
        the person and organization graphs. This is the trickiest part of this
        method.

        Because we never want to remote URIs from the graph that we've minted,
        but we want to keep the triples in our graphs up to date, we'll want to
        remove triples like:

            <person> isCreatorOf <somedataset>

        but not

            <person> hasFirstName 'Spike'
        """

        if 'datasets' not in self.stores:
            raise Exception("Datasets store not found.")

        datasets = self.stores['datasets']

        if 'people' not in self.stores:
            raise Exception("People store not found.")

        people = self.stores['people']

        if 'organizations' not in self.stores:
            raise Exception("Organizations store not found.")

        organizations = self.stores['organizations']


        identifier = doc.find(".//str[@name='identifier']").text
        identifier_esc = urllib.quote_plus(identifier)

        # Dataset itself
        store.delete_by_subject('d1resolve:'+identifier_esc)

        # The Dataset's identifier
        delete_identifier_query = """
        DELETE
        WHERE {
            ?b ?p ?o .
            ?b %s '%s'
        }
        """ % (self.ns_interp('glview:'+'hasIdentifierValue'), identifier)

        datasets.update(delete_identifier_query)

        # Digital Objects
        delete_digital_objects_query = """
        DELETE
        WHERE {
            ?s %s %s
        }
        """ % (self.ns_interp('glview:'+'isPartOf'), self.ns_interp('d1resolve:'+urllib_quote_plus(identifier)))

        datasets.update(delete_digital_objects_query)

        # Remove any isCreatorOf for this dataset
        # In both people and organizations

        delete_is_creator_of_query = """
        DELETE
        WHERE {
            ?s %s %s
        }
        """ % (self.ns_interp('glview:'+'isCreatorOf'), self.ns_interp('d1resolve:'+urllib_quote_plus(identifier)))


    def addPersonTriples(self, uri, record):
        if 'people' not in self.stores:
            raise Exception("People store not found.")

        store = self.stores['people']


        if 'salutation' in record:
            store.add([uri, 'glview:namePrefix', record['salutation']])

        if 'full_name' in record:
            store.add([uri, 'glview:nameFull', record['full_name']])

        if 'first_name' in record:
            store.add([uri, 'glview:nameGiven', record['first_name']])

        if 'last_name' in record:
            store.add([uri, 'glview:nameFamily', record['last_name']])

        if 'organization' in record:
            print "organization is in record"
            if self.organizationExists(record['organization']):
                organization_uri = self.findOrganization(record['organization'])
                print "used existing uri"
            else:
                organization_uri = self.mintURI('d1org')
                print "minted new URI"

            print organization_uri

            store.add([uri, 'glview:hasAffiliation', organization_uri])

        if 'email' in record:
            store.add([uri, 'foaf:mbox', '<mailto:'+record['email']+'>'])

        if 'address' in record:
            store.add([uri, 'glview:address', record['address']])

        if 'document' in record:
            store.add([uri, 'glview:isCreatorOf', 'd1resolve:' + record['document']])


    def addOrganizationTriples(self, uri, record):
        if 'organizations' not in self.stores:
            raise Exception("Datasets store not found.")

        store = self.stores['organizations']


        if 'name' in record:
            store.add([uri, 'rdfs:label', record['name']])

        if 'email' in record:
            store.add([uri, 'foaf:mbox', '<mailto:'+record['email']+'>'])

        if 'address' in record:
            store.add([uri, 'glview:address', record['address']])

        if 'document' in record:
            store.add([uri, 'glview:isCreatorOf', 'd1resolve:' + record['document']])


    def mintURI(self, ns):
        if ns not in self.ns:
            raise Exception("URI string passed to mintURI that didn't exist in the namespace mappings.")

        return "%s:urn:uri:%s" % (self.ns_interp(ns), str(uuid.uuid4()))


    def get_key(self, record):
        """
        Generates a key (or None if invalid record) for deduplicating the
        record.
        """

        key = None

        if 'type' not in record:
            return key

        if record['type'] == "person":
            if 'last_name' in record and 'email' in record and len(record['last_name']) > 0 and len(record['email']) > 0:
                key  = "%s#%s" % (record['last_name'], record['email'])
        elif record['type'] == "organization":
            if 'name' in record and len(record['name']) > 0:
                key  = "%s" % (record['name'])

        return key
