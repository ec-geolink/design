import requests
import os
import uuid

from d1graphservice import util


class Store():
    """
    Wrapper class that can be used to query a Jena endpoint that speaks Fuseki.
    """

    def __init__(self, endpoint, dataset, ns):
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
        self.ns = ns


    def ns_interp(self, text):
        """
        Helper function to call util.ns_interp without having to specify
        namespaces.

        Arguments:
            text: str
                The text to interpolate, i.e., 'example:foo'
        """

        return util.ns_interp(text, self.ns)


    def query(self, query):
        """
        Execute a SPARQL QUERY.
        """

        r = requests.get(self.query_url, params={ 'query': query.encode('utf-8') })

        print query.strip()

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

        """ Process object string.
            If it doesn't start with a <, make it a string literal.
        """

        object_string = self.ns_interp(triple[2])

        if object_string is None:
            raise Exception("Object string interpolation failed.")

        if not object_string.startswith("<"):
            object_string = "'%s'" % object_string


        q = """
        INSERT DATA { %s %s %s }
        """ % (self.ns_interp(triple[0]), self.ns_interp(triple[1]), object_string)
        print q.strip()
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


    def delete_all(self):
        """
        Delete all triples in the dataset.
        """

        self.delete(['?s', '?p', '?o'])


    def delete(self, triple):
        """
        Deletes a triple.
        """

        q = """
        DELETE { ?s ?p ?o }
        WHERE { %s %s %s }
        """ % (self.ns_interp(triple[0]), self.ns_interp(triple[1]), self.ns_interp(triple[2]))

        print q.strip()

        r = self.update(q)


    def delete_by_subject(self, subject):
        """
        Delete all triples with the given subject.
        The subject argument should be a URI string.
        """

        q = """
        DELETE
        WHERE { %s ?p ?o}
        """ % self.ns_interp(subject)

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


if __name__ == "__main__":
    """
    Prior to creating a Store,
    fuseki-server --update --mem /ds
    s-put http://localhost:3030/ds/data default ../../organizations.ttl
    s-put http://localhost:3030/ds/data default ../../people.ttl
    """

    s = Store("http://localhost:3131/", 'ds')
