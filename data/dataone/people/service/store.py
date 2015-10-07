import requests
import os


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


    def query(self, query):
        """
        Execute a SPARQL QUERY.
        """

        r = requests.get(self.query_url, params={ 'query': query })

        print "Query (Status: %s): %s" % (r.status_code, query)

        return r


    def update(self, query):
        """
        Execute a SPARQL UPDATE.
        """

        r = requests.post(self.update_url, data=query)

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
        PREFIX glview: <http://schema.geolink.org/dev/view/>
        INSERT DATA { %s %s %s }
        """ % (triple[0], triple[1], triple[2])

        print "add()"
        print q
        print self.count()
        self.update(q)
        print self.count()



    def find(self, conditions):
        """
        Finds records with the given set of conditions.

        Conditions are a Dict of the form { 'predicate': 'object'}.

            e.g. conditions = { 'foaf:mbox': '<mailto:myemail@me.com>' }
        """

        q = """
        PREFIX glview: <http://schema.geolink.org/dev/view/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?subject
        """

        where_strings = []

        for predicate in conditions:
            object_string = conditions[predicate]

            if not object_string.startswith("<"):
                object_string = "'%s'" % object_string

            where_string = "?subject %s %s" % (predicate, object_string)
            where_strings.append(where_string)

        where_clause = " WHERE { %s }" % " . ".join(where_strings)
        q += where_clause

        response = self.query(q).json()

        return response['results']['bindings']


    def findPerson(self, family, email):
        """
        Finds a person by their family name and email.
        """

        condition = {
            'glview:nameFamily': family,
            'foaf:mbox': "<mailto:%s>" % email
        }

        return self.find(condition)


    def personExists(self, family, email):
        """
        Returns True or False whether the person with the given family name
        and email exists (has a URI).
        """

        result = self.findPerson(family, email)

        if len(result) == 1:
            return True
        else:
            return False


    def findOrganization(self, name):
        """
        Finds an organization by their name.
        """

        condition = {
            'rdf:label': name,
        }

        return self.find(condition)


    def organizationExists(self, name):
        """
        Returns True or False whether the organization with the given name
        exists (has a URI).
        """

        result = self.findOrganization(name)

        if len(result) == 1:
            return True
        else:
            return False


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

        q = """
        DELETE
        WHERE { <%s> ?p ?o}
        """ % subject

        r = self.update(q)


    def delete_by_object(self, object):
        """
        Delete all triples with the given object.
        The object argument should be a URI string.
        """

        q = """
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

        result = s.query(q).text

        print "Exporting all triples to %s" % filename

        with open(filename, "wb") as f:
            f.write(result.encode("utf-8"))

        size = os.stat(filename).st_size

        print "Exported %d bytes." % size


if __name__ == "__main__":
    """
    Prior to creating a Store,
    fuseki-server --update --mem /ds
    s-put http://localhost:3030/ds/data default ../../organizations.ttl
    s-put http://localhost:3030/ds/data default ../../people.ttl
    """

    s = Store("http://localhost:3030/", 'ds')


    s.add(['glview:X', 'glview:type', 'glview:Y'])

    # s.export("people_and_organizations.ttl")
