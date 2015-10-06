"""
Wrapper class that can be used to query a Jena endpoint that speaks Fuseki.
"""

import requests


class Store():
    """
    """

    def __init__(self, endpoint, dataset):
        """
        """

        # Strip surrounding slashes in arguments
        self.dataset = dataset.strip("/")
        self.endpoint = endpoint.strip("/")

        # Set aside query URLs for QUERY and UPDATE requestes
        self.query_url  = '/'.join([self.endpoint, self.dataset, 'query'])
        self.update_url  = '/'.join([self.endpoint, self.dataset, 'update'])


    def query(self, query):
        """
        """

        r = requests.get(self.query_url, params={ 'query': query })

        return r


    def update(self, query):
        """
        """

        r = requests.post(self.update_url, data=query)

        return r


    def count(self):
        """
        """

        q = """
        SELECT (COUNT(*) AS ?num) { ?s ?p ?o  }
        """

        r = self.query(q)
        response = r.json()

        return int(response['results']['bindings'][0]['num']['value'])


    def all(self):
        """
        """

        q = """
        SELECT * {?s ?p ?o}
        """

        r = self.query(q)
        response = r.json()

        return response['results']['bindings']


    def delete_all(self):
        """
        """

        q = """
        DELETE { ?s ?p ?o }
        WHERE { ?s ?p ?o}
        """

        r = self.update(q)


    def delete_by_subject(self, subject):
        """
        """

        q = """
        DELETE
        WHERE { <%s> ?p ?o}
        """ % subject

        r = self.update(q)


if __name__ == "__main__":
    s = Store("http://localhost:3030/", 'ds')

    print s.count()

    records = s.all()

    if len(records) > 0:
        first = records[0]
        first_subject = first['s']['value']

        s.delete_by_subject(first_subject)

    print s.count()
