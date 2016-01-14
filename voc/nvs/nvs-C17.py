from rdflib import Graph, OWL, URIRef, RDF, RDFS, Literal, Namespace, BNode
from rdflib.namespace import SKOS, DC, DCTERMS

datapath = "./"
rootURIString = "http://schema.geolink.org/1.0/voc/nvs/"
parentcollectionname = "L06"
collectionname = "C17"
graphURIString = datapath + collectionname + "-source.rdf"
g = Graph()
result = g.parse(graphURIString)

print(graphURIString, "has %s statements." % len(g))

# s = g.serialize(format='turtle').splitlines()
# for l in s:
#     if l: print(l.decode('utf-8'))

## load parent collection
parentGraph = Graph()
parentGraph.parse(datapath + parentcollectionname + "-source.rdf")
parentCollectionURI = parentGraph.value(None, RDF.type, SKOS.Collection)
parentcollectionOntologyURI = URIRef(rootURIString + parentcollectionname)

print((datapath + parentcollectionname + "-source.rdf"), "has %s statements." % len(parentGraph))

## write as OWL

## prepare namespace
idschemeOntoNs = Namespace("http://schema.geolink.org/1.0/voc/identifierscheme#")
## define appropriate idscheme
## the identifier scheme is assumed to already be defined in identifierscheme.owl
idscheme = idschemeOntoNs.sdn


ontologyURIString = rootURIString + collectionname
defaultNS = Namespace(ontologyURIString + '#')
glbaseNS = Namespace('http://schema.geolink.org/1.0/base/main#')
comment = "This ontology captures ICES platform instances from the NERC vocabulary server"
ontologyCreator = "EarthCube GeoLink project"

owloutput = Graph()
owloutput.bind('', defaultNS)
owloutput.bind('glbase', glbaseNS)
owloutput.bind('owl', OWL)
owloutput.bind('dcterms', DCTERMS)
owloutput.bind('dc', DC)
owloutput.bind('skos', SKOS)
owloutput.bind('idscheme', idschemeOntoNs)


## write ontology header
ontologyURI = URIRef(ontologyURIString)
owloutput.add((ontologyURI, RDF.type, OWL.Ontology))

collectionURI = g.value(None, RDF.type, SKOS.Collection)
owloutput.add((ontologyURI, RDFS.seeAlso, collectionURI))
for m in g.objects(collectionURI, DCTERMS.date):
    owloutput.add((ontologyURI, DCTERMS.date, m))
for m in g.objects(collectionURI, DCTERMS.title):
    owloutput.add((ontologyURI, RDFS.label, m))
    owloutput.add((ontologyURI, DCTERMS.title, m))
owloutput.add((ontologyURI, DCTERMS.creator, Literal(ontologyCreator, lang='en')))

owloutput.add((ontologyURI, RDFS.comment, Literal(comment, lang='en')))

## imports L06.owl
owloutput.add((ontologyURI, OWL.imports, parentcollectionOntologyURI))

## adding object property glbase:hasIdentifier,
## glbase:hasIdentifierScheme, glbase:hasIdentifierValue
owloutput.add((glbaseNS.hasIdentifier, RDF.type, OWL.ObjectProperty))
owloutput.add((glbaseNS.hasIdentifierScheme, RDF.type, OWL.ObjectProperty))
owloutput.add((glbaseNS.hasIdentifierValue, RDF.type, OWL.DatatypeProperty))


## adding class glbase:Platform
owloutput.add((glbaseNS.Platform, RDF.type, OWL.Class))


# ## add each member of the L06 collection, i.e., platform types to ontology as instances of PlatformType
# ## and pun them as OWL Classes too;
colcreator = g.value(collectionURI, DCTERMS.creator, None)
for platform in g.objects(collectionURI, SKOS.member):
    owloutput.add((platform, RDF.type, OWL.NamedIndividual))
    platformtypeFound = False
    for platformtype in g.objects(platform, SKOS.broader):
        if platformtype and (parentCollectionURI, SKOS.member, platformtype) in parentGraph:
            owloutput.add((platformtype, RDF.type, OWL.Class))
            owloutput.add((platform, RDF.type, platformtype))
            platformtypeFound = True
    if not platformtypeFound:
        owloutput.add((platform, RDF.type, glbaseNS.Platform))

    ## add deprecation status if any
    depre = g.value(platform, OWL.deprecated, None)
    if depre:
        # if str(depre) == 'true': print(instrumenttype, depre)
        owloutput.add((platform, OWL.deprecated, depre))

    label = g.value(platform, SKOS.prefLabel, None)
    owloutput.add((platform, RDFS.label, label)) # add the pref-label as rdfs:label in the ontology
    definition = g.value(platform, SKOS.definition, None)
    owloutput.add((platform, RDFS.comment, definition)) # add skos definition as rdfs:comment in the onto
    date = g.value(platform, DCTERMS.date, None)
    owloutput.add((platform, DCTERMS.date, date)) # add original definition date of platform to onto
    owloutput.add((platform, DCTERMS.creator, colcreator))

    # add identifier
    bn = BNode()
    ident = g.value(platform, DCTERMS.identifier, None)
    owloutput.add((platform, glbaseNS.hasIdentifier, bn))
    owloutput.add((bn, glbaseNS.hasIdentifierValue, ident))
    ## we assume idschemeOntoNs.sdnl06 as the identifier scheme for the platform types (SeaDataNet L06)
    ## the identifier scheme is assumed to already be defined in identifierscheme.owl
    owloutput.add((bn, glbaseNS.hasIdentifierScheme, idscheme))


s = owloutput.serialize(format='turtle', encoding='utf-8').splitlines()
fout = open(datapath + collectionname + ".owl",'w',newline='\n')
for l in s:
    if l:
        # print(l.decode('utf-8'))
        fout.write(l.decode('utf-8'))
        fout.write('\n')

fout.close()
