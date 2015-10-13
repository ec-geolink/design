import requests
import os
import uuid

from service import util


class Store():
    """
    Wrapper class that can be used to query a Jena endpoint that speaks Fuseki.
    """

    def __init__(self, endpoint, dataset):
        """
        Stores the dataset name and SPARQL endpoint URL and prepopulates
        SPARQL QUERY and UPDATE URLs for executing SPARQL queries.
        """

        # Strip surrounding slashes in arguments
        self.dataset = dataset.strip("/")
        self.endpoint = endpoint.strip("/")

        # Set aside query URLs for QUERY and UPDATE requestes
        self.query_url  = '/'.join([self.endpoint, self.dataset, 'query'])
        self.update_url  = '/'.join([self.endpoint, self.dataset, 'update'])

        # Namespaces
        self.ns = {
            "foaf": "http://xmlns.com/foaf/0.1/",
            "dcterms": "http://purl.org/dc/terms/",
            "datacite": "http://purl.org/spar/datacite/",
            "owl": "http://www.w3.org/2002/07/owl#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "glview": "http://schema.geolink.org/dev/view/",
            "d1people": "https://dataone.org/person/",
            "d1org": "https://dataone.org/organization/",
            "d1resolve": "https://cn.dataone.org/cn/v1/resolve/"
        }


    def mintURI(self, ns):
        return "%s:urn:uri:%s" % (ns, str(uuid.uuid4()))


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


    def ns_interp(self, text):
        """
        Triple strings (e.g. foo:Bar) have to be expanded because SPARQL queries
        can't handle the subject of a triple being

            d1resolve:doi:10.6073/AA/knb-lter-pie.77.3

        but can handle

            <https://cn.dataone.org/cn/v1/resolve/doi:10.6073/AA/knb-lter-pie.77.3>

        This method does that interpolation using the class instance's
        namespaces.
        """

        if self.ns is None or len(self.ns) == 0:
            print "No namespaces to interpolate with."
            return text

        colon_index = text.find(":")

        if len(text) <= colon_index + 1:
            return text

        namespace = text[0:colon_index]
        rest = text[(colon_index)+1:]

        if namespace not in self.ns:
            return text

        return "<%s%s>" % (self.ns[namespace], rest)


    def query(self, query):
        """
        Execute a SPARQL QUERY.
        """

        r = requests.get(self.query_url, params={ 'query': query.encode('utf-8') })

        # print "Query (Status: %s): %s" % (r.status_code, query)

        return r


    def update(self, query):
        """
        Execute a SPARQL UPDATE.
        """

        r = requests.post(self.update_url, data=query.encode('utf-8'))

        return r


    def count(self):
        """
        Return the number of triples in dataset.
        """

        q = """
        SELECT (COUNT(*) AS ?num) { ?s ?p ?o  }
        """

        r = self.query(q)
        response = r.json()

        return int(response['results']['bindings'][0]['num']['value'])


    def all(self):
        """
        Return all triples in the dataset.
        """

        q = """
        SELECT * {?s ?p ?o}
        """

        r = self.query(q)
        response = r.json()

        return response['results']['bindings']


    def add(self, triple):
        """
        Adds triple to the graph using an update query.
        """

        if type(triple) is not list and len(triple) != 3:
            print "Failed to add triple: Expected triple argument to be an array of size 3."
            return

        q = """
        INSERT DATA { %s %s %s }
        """ % (self.ns_interp(triple[0]), self.ns_interp(triple[1]), self.ns_interp(triple[2]))
        print q
        self.update(q)


    def exists(self, triple):
        """
        Check if the triple exists.
        """

        if type(triple) is not list and len(triple) != 3:
            print "Failed to check triple for existence: Expected triple argument to be an array of size 3."
            return

        q = """
        SELECT (COUNT(*) AS ?num) {%s %s %s}
        """ % (self.ns_interp(triple[0]), self.ns_interp(triple[1]), self.ns_interp(triple[2]))

        r = self.query(q).json()

        if len(r['results']['bindings']) == 1 and r['results']['bindings'][0]['num']['value'] == u'1':
            return True

        return False





    def find(self, conditions):
        """
        Finds records with the given set of conditions.

        Conditions are a Dict of the form { 'predicate': 'object'}.

            e.g. conditions = { 'foaf:mbox': '<mailto:myemail@me.com>' }
        """

        q = """
        SELECT ?subject
        """

        where_strings = []

        for predicate in conditions:
            object_string = self.ns_interp(conditions[predicate])

            if not object_string.startswith("<"):
                object_string = "'%s'" % object_string

            where_string = "?subject %s %s" % (self.ns_interp(predicate), object_string)
            where_strings.append(where_string)

        where_clause = " WHERE { %s }" % " . ".join(where_strings)
        q += where_clause

        print q
        response = self.query(q).json()

        print response

        return response['results']['bindings']


    def findPerson(self, family, email):
        """
        Finds a person by their family name and email.
        """

        condition = {
            'glview:nameFamily': family,
            'foaf:mbox': "<mailto:%s>" % email
        }

        find_result = self.find(condition)

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

        condition = {
            'rdf:label': name,
        }

        find_result = self.find(condition)

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


    def delete_all(self):
        """
        Delete all triples in the dataset.
        """

        q = """
        DELETE { ?s ?p ?o }
        WHERE { ?s ?p ?o}
        """

        r = self.update(q)


    def delete_by_subject(self, subject):
        """
        Delete all triples with the given subject.
        The subject argument should be a URI string.
        """

        q = self.ns
        q += """
        DELETE
        WHERE { <%s> ?p ?o}
        """ % subject

        r = self.update(q)


    def delete_by_object(self, object):
        """
        Delete all triples with the given object.
        The object argument should be a URI string.
        """

        q = self.ns
        q += """
        DELETE
        WHERE { ?s ?p <%s> }
        """ % object

        r = self.update(q)


    def export(self, filename):
        """
        Exports the Store as a Turtle file.
        """

        if os.path.isfile(filename):
            print "File at `%s` already exists. Delete this file first." % filename
            return

        q = """
        DESCRIBE ?s ?p ?o
        WHERE { ?s ?p ?o }
        """

        result = self.query(q).text

        print "Exporting all triples to %s" % filename

        with open(filename, "wb") as f:
            f.write(result.encode("utf-8"))

        size = os.stat(filename).st_size

        print "Exported %d bytes." % size


    def addPerson(self, record):
        key = self.get_key(record)

        if key is None:
            person_uri = self.mintURI('d1people')
        else:
            last,email = key.split("#")

            if self.personExists(last, email):
                person_uri = self.findPerson(last, email)

            else:
                person_uri = self.mintURI('d1people')

        self.addPersonTriples(person_uri, record)


    def addOrganization(self, record):
        key = record['name']

        if key is None:
            organization_uri = self.mintURI('d1org')

        else:
            if self.organizationExists(key):
                organization_uri  = self.findOrganization(key)
            else:
                print "  notexist"
                organization_uri = self.mintURI('d1org')

        self.addOrganizationTriples(organization_uri, record)


    def addDataset(self):
    def addDataset(self, doc):
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

        if any(['d1resolve:'+identifier, '?p', '?o']):
            self.deleteDatasetTriples(doc, scimeta, formats)

        self.addDatasetTriples(doc, scimeta, formats)




    def addDatasetTriples(self, doc, scimeta, formats = {}):
        """

        """
        identifier = doc.find(".//str[@name='identifier']").text

        # type Dataset
        self.add(['d1resolve:'+identifier, 'rdf:type', 'glview:Dataset'])


        # Title
        title_element = doc.find("./str[@name='title']")

        if title_element is not None:
            self.add(['d1resolve:'+identifier, 'glview:title', title_element.text])
            self.add(['d1resolve:'+identifier, 'rdf:label', title_element.text])

        # Add glview Identifier
        id_blank_node = "<_:%s>" % identifier

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

        self.add([id_blank_node, 'rdf:type', 'glview:Identifier'])
        self.add([id_blank_node, 'glview:hasIdentifierValue', identifier])
        self.add([id_blank_node, 'glview:hasIdentifierValue', "'%s'" % identifier])
        self.add([id_blank_node, 'rdfs:label', identifier])
        self.add([id_blank_node, 'glview:hasIdentifierScheme', 'datacite:'+scheme])

        self.add(['d1resolve:'+identifier, 'glview:hasIdentifier', id_blank_node])

        # Abstract
        abstract_element = doc.find("./str[@name='abstract']")

        if (abstract_element is not None):
            self.add(['d1resolve:'+identifier, 'glview:description', abstract_element.text])


        # For digital Object in this dataset
        #self.addDigitalObject(identifier, digital_object, formats)
        # Digital Objects
        digital_objects = doc.findall("./arr[@name='documents']/str")

        for digital_object in digital_objects:
            self.addDigitalObject(identifier, digital_object, formats)


    def deleteDatasetTriples(self):
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

        print "deleteDataset"


    def addDigitalObject(self, identifier, digital_object, formats):
        """
        """

        self.addDigitalObjectTriples(identifier, digital_object, formats)


    def addDigitalObjectTriples(self, identifier, digital_object, formats):
        """
        Notes:
            Creates only two triples (type and isPartOf) if the scimeta for the
            digital object can't be retrieved off the CN.
        """

        data_id = digital_object.text

        self.add(['d1base:'+data_id, 'rdf:type', 'glview:DigitalObject'])
        self.add(['d1base:'+data_id, 'glview:isPartOf', 'd1base'+identifier])

        # Get data object meta
        data_meta = util.getXML("https://cn.dataone.org/cn/v1/meta/" + data_id)

        if data_meta is None:
            print "Metadata for data object %s was not found. Continuing to next data object." % data_id
            return

        # Checksum and checksum algorithm
        checksum_node = data_meta.find(".//checksum")

        if checksum_node is not None:
            self.add(['d1base:'+data_id, 'glview:hasChecksum', checksum_node.text])
            self.add(['d1base:'+data_id, 'glview:hasChecksumAlgorithm', checksum_node.get("algorithm")])

        # Size
        size_node = data_meta.find("./size")

        if size_node is not None:
            self.add(['d1base:'+data_id, 'glview:hasByteLength', size_node.text])

        # Format
        format_id_node = data_meta.find("./formatId")

        if format_id_node is not None:
            if format_id_node.text in formats:
                self.add(['d1base:'+data_id, 'glview:hasFormat', formats[format_id_node.text]['uri']])

            else:
                print "Format not found."


        # Date uploaded
        date_uploaded_node = data_meta.find("./dateUploaded")

        if date_uploaded_node is not None:
            self.add(['d1base:'+data_id, 'glview:dateUploaded', date_uploaded_node.text])


        # Submitter and rights holders
        # submitter_node = data_meta.find("./submitter")
        #
        # if submitter_node is not None:
        #     submitter_node_text = " ".join(re.findall(r"o=(\w+)", submitter_node.text, re.IGNORECASE))
        #
        #     if len(submitter_node_text) > 0:
        #         self.add(['d1base:'+data_id, 'glview:hasCreator', ])


        # rights_holder_node = data_meta.find("./rightsHolder")
        #
        # if rights_holder_node is not None:
        #     rights_holder_node_text = " ".join(re.findall(r"o=(\w+)", rights_holder_node.text, re.IGNORECASE))
        #
        #     if len(rights_holder_node_text) > 0:
        #         addStatement(model, d1base+data_id, ns["glbase"]+"hasRightsHolder", RDF.Uri("urn:node:" + rights_holder_node_text.upper()))



    def addPersonTriples(self, uri, record):
        print "addPersonTriples"

        if 'salutation' in record:
            self.add([uri, 'glview:namePrefix', "'%s'" % record['salutation']])

        if 'full_name' in record:
            self.add([uri, 'glview:nameFull', "'%s'" % record['full_name']])

        if 'first_name' in record:
            self.add([uri, 'glview:nameGiven', "'%s'" % record['first_name']])

        if 'last_name' in record:
            self.add([uri, 'glview:nameFamily', "'%s'" % record['last_name']])

        #TODO
        #find or mint org uri
        # record['organization']
        #
        # if 'organization' in record:
        #     self.add([uri, 'glview:nameFull', ])
        if 'organization' in record:
            if self.exists(['?s', 'rdf:label', record['organization']]):
                print 'exists'
            # org_uri =
            # self.add([uri, 'glview:hasAffiliation', org_uri])

        if 'email' in record:
            self.add([uri, 'foaf:mbox', '<mailto:'+record['email']+'>'])

        if 'address' in record:
            self.add([uri, 'glview:address', "'%s'" % record['address']])

        if 'document' in record:
            self.add([uri, 'glview:isCreatorOf', 'd1resolve:' + record['document']])


    def addOrganizationTriples(self, uri, record):
        print "addOrganizationTriples"

        if 'name' in record:
            self.add([uri, 'rdf:label', "'%s'" % record['name']])

        if 'email' in record:
            self.add([uri, 'foaf:mbox', '<mailto:'+record['email']+'>'])

        if 'address' in record:
            self.add([uri, 'glview:address', "'%s'" % record['address']])

        if 'document' in record:
            self.add([uri, 'glview:isCreatorOf', 'd1resolve:' + record['document']])


if __name__ == "__main__":
    """
    Prior to creating a Store,
    fuseki-server --update --mem /ds
    s-put http://localhost:3030/ds/data default ../../organizations.ttl
    s-put http://localhost:3030/ds/data default ../../people.ttl
    """

    s = Store("http://localhost:3030/", 'ds')

    print s.count()

    # s.export("people_and_organizations.ttl")
