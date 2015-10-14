# Harvester Proposal

This proposal describes Harvester Service for the GeoLink project.

The Harvester Service serves the purpose of keeping the unified (all members)
GeoLink graph up to date with the graphs from GeoLink member repositories. To do
this, the Harvester Service retrieves graphs from GeoLink member repositories
and imports them into a central triple store.


## Harvesting From Member Repositories

**What exactly will be located at each member repository?**

Each member repository is responsible for maintaining a single graph which
contains triples for information that has been updated since the harvester
service last visited that member repository. The need of just the changed
triples rather than all triples is one of efficiency. Member repository graphs
may contain millions of triples but the vast majority of these will only need to
be imported into the central triple store once and never changed. By requiring
member repositories to maintain only a set of only the triples that have changed
since the Harvester Service last visited the member repository, we reduce the
time it will take to retrieve graphs from the member repositories and integrate
those changes into the Harvester's central triple store


**How will harvesting be coordinated?**

The Harvester Service needs to know where to find a graph at a member repository
and which named graph to import it into in the central triple store. Rather than
hard-code this information into the service, we will use existing semantics from
the [SPARQL 1.1 Service
Description](http://www.w3.org/TR/sparql11-service-description/) specification,
which extends work from the [VoID
Vocabulary](http://www.w3.org/TR/2011/NOTE-void-20110303/), to describe the
member repository graphs and instruct the Harvester Service on how to harvest
triples from them.

```{ttl}
<#GeolinkSPARQL> a sd:Service;
    sd:url <http://data.geolink.org/sparql>;
    sd:defaultDatasetDescription [
        a sd:Dataset;
        dcterms:title “GeoLink Public SPARQL Endpoint";
        dcterms:description "A good description of GeoLink";
        sd:defaultGraph [
            a sd:Graph, void:Dataset;
            dcterms:title “GeoLink Graph and Dataset Descriptions";
            dcterms:description "Contains a copy of this SD+VoID file!";
        ];
        sd:namedGraph [
            sd:name <http://data.geolink.org/id/r2r>;
            sd:graph [
                a sd:Graph, void:Dataset;
                dcterms:title “R2R Graph";
                void:dataDump <http://wsu.edu/r2r_enhanced_dump.rdf>;
            ];
        ];
```

The Harvester Service will query the GeoLink SPARQL endpoint for named graphs at
some interval and visit the data dumps it finds, processing the graphs and
importing triples from them.


## Updating the Central Triple Store

**How will the the triples be processed?**

When the Harvester Service visits a member repository, it may find either an
empty or non-empty graph of changed triples. When it finds a non-empty graph of
changed triples, it should make a list of all of the unique subjects of those
triples, delete from the central triple store all triples with those subjects,
and finish by adding the changed triples to the central triple store.

This can be illustrated in an example. If the central triple store contains
information on three people and their names,

```{ttl}
# Central triple store
example:Bob foaf:name 'Bob' .
example:Alice foaf:name 'Alice' .
example:Jane foaf:name 'Jane' .
```

And a member repository needs to add that the person also has an email address,

```{ttl}
# Member graph
example:Alice foaf:name 'Alice' ;
              foaf:mbox <alice@example.org> .
```

then the triple `example:Alice foaf:name 'Alice'` in the central triple store
would be deleted because it has the subject `example:Alice` (which is in the
member graph). Then the two triples about Alice from the member graph would be
inserted into the central triple store.

In specifying the member graphs this way, we are assuming that, if a particular
URI exists as a subject in the member graph, that the member graph is presenting
all the information it knows about that URI and not just information that has
changed since the graph was last generated. If the member graph had contained
only the following triple:

```{ttl}
# Member graph
example:Alice foaf:mbox <alice@example.org> .
```

Then that would imply that Alice's name is no longer 'Alice' but that she does
have an email address, `<alice@example.org>` and the central triple store would
no longer contain a triple that Alice's `foaf:name` is 'Alice'.
