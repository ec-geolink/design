from rdflib import Graph, OWL, URIRef, RDF, RDFS, Literal, Namespace, BNode
from rdflib.namespace import SKOS, DC, DCTERMS

datapath = "./"
directUpperCollectionName = "P03"
uppergraph = Graph()
uppergraph.parse(datapath + directUpperCollectionName + "-source.rdf")
upperCollectionURI = uppergraph.value(None, RDF.type, SKOS.Collection)
upperCollectionOntologyNs = Namespace("http://schema.geolink.org/1.0/voc/nvs/" + directUpperCollectionName + "#")
upperCollectionOntologyURI = URIRef("http://schema.geolink.org/1.0/voc/nvs/" + directUpperCollectionName)

collectionname = "P02"
graphURIString = datapath + collectionname + "-source.rdf"
g = Graph()
result = g.parse(graphURIString)

print(graphURIString, "has %s statements." % len(g))

# s = g.serialize(format='turtle').splitlines()
# for l in s:
#     if l: print(l.decode('utf-8'))

## write as OWL
idschemeOntoNs = Namespace("http://schema.geolink.org/1.0/voc/identifierscheme#")
## define appropriate idscheme
## the identifier scheme is assumed to already be defined in identifierscheme.owl
idscheme = idschemeOntoNs.SDNP02

ontologyURIString = "http://schema.geolink.org/1.0/voc/nvs/" + collectionname
defaultNS = Namespace(ontologyURIString + '#')
glbaseNS = Namespace('http://schema.geolink.org/1.0/base/main#')
comment = "This ontology captures SeaDataNet device catalog from the NERC vocabulary server with mapping to SeaDataNet device categories"
ontologyCreator = "EarthCube GeoLink project"
owloutput = Graph()
owloutput.bind('', defaultNS)
owloutput.bind('glbase', glbaseNS)
owloutput.bind('owl', OWL)
owloutput.bind('dcterms', DCTERMS)
owloutput.bind('dc', DC)
owloutput.bind('skos', SKOS)
owloutput.bind('idscheme', idschemeOntoNs)

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

## importing upper collection ontology
owloutput.add((ontologyURI, OWL.imports, upperCollectionOntologyURI))

## adding object property glbase:hasMeasurementType, glbase:hasIdentifier,
## glbase:hasIdentifierScheme, glbase:hasIdentifierValue
owloutput.add((glbaseNS.hasMeasurementType, RDF.type, OWL.ObjectProperty))
owloutput.add((glbaseNS.hasIdentifier, RDF.type, OWL.ObjectProperty))
owloutput.add((glbaseNS.hasIdentifierScheme, RDF.type, OWL.ObjectProperty))
owloutput.add((glbaseNS.hasIdentifierValue, RDF.type, OWL.DatatypeProperty))

## adding class P03:SeaDataNetParameter, glbase:MeasurementType
owloutput.add((upperCollectionOntologyNs.SeaDataNetParameter, RDF.type, OWL.Class))
owloutput.add((glbaseNS.MeasurementType, RDF.type, OWL.Class))


## add each member of the P02 collection, i.e., Measurement types to ontology as instances of MeasurementType
## and pun them as OWL Classes too;
colcreator = g.value(collectionURI, DCTERMS.creator, None)
for measurementtype in g.objects(collectionURI, SKOS.member):
    owloutput.add((measurementtype, RDF.type, OWL.NamedIndividual))
    owloutput.add((measurementtype, RDF.type, OWL.Class))
    owloutput.add((measurementtype, RDF.type, glbaseNS.MeasurementType))

    ## add deprecation status if any
    depre = g.value(measurementtype, OWL.deprecated, None)
    if depre:
        # if str(depre) == 'true': print(instrumenttype, depre)
        owloutput.add((measurementtype, OWL.deprecated, depre))

    ## add typecasting axiom
    bn1 = BNode()
    bn2 = BNode()
    lst = BNode()
    owloutput.add((bn1, RDF.type, OWL.Restriction))
    owloutput.add((bn1, OWL.onProperty, glbaseNS.hasMeasurementType))
    owloutput.add((bn1, OWL.someValuesFrom, bn2))
    owloutput.add((bn2, RDF.type, OWL.Class))
    owloutput.add((bn2, OWL.oneOf, lst))
    owloutput.add((lst, RDF.first, measurementtype))
    owloutput.add((lst, RDF.rest, RDF.nil))
    owloutput.add((bn1, RDFS.subClassOf, measurementtype))

    label = g.value(measurementtype, SKOS.prefLabel, None)
    owloutput.add((measurementtype, RDFS.label, label)) # add the pref-label as rdfs:label in the ontology
    definition = g.value(measurementtype, SKOS.definition, None)
    owloutput.add((measurementtype, RDFS.comment, definition)) # add skos definition as rdfs:comment in the onto
    date = g.value(measurementtype, DCTERMS.date, None)
    owloutput.add((measurementtype, DCTERMS.date, date)) # add original definition date of measurementtype to onto
    owloutput.add((measurementtype, DCTERMS.creator, colcreator))
    # add identifier
    bn = BNode()
    ident = g.value(measurementtype, DCTERMS.identifier, None)
    owloutput.add((measurementtype, glbaseNS.hasIdentifier, bn))
    owloutput.add((bn, glbaseNS.hasIdentifierValue, ident))
    owloutput.add((bn, glbaseNS.hasIdentifierScheme, idscheme))

    ## get equivclass
    for equivcls in g.objects(measurementtype, OWL.sameAs):
        if (collectionURI, SKOS.member, equivcls) in  g:
            owloutput.add((measurementtype, OWL.equivalentClass, equivcls))
    ## get subclass
    for subcls in g.objects(measurementtype, SKOS.narrower):
        if (collectionURI, SKOS.member, subcls) in g:
            owloutput.add((subcls, RDFS.subClassOf, measurementtype))
    ## get superclass
    isSubclassedToDefaultSuperClass = True
    for supcls in g.objects(measurementtype, SKOS.broader):
        if (collectionURI, SKOS.member, supcls) in g:
            owloutput.add((measurementtype, RDFS.subClassOf, supcls))
            isSubclassedToDefaultSuperClass = False
        elif (upperCollectionURI, SKOS.member, supcls) in uppergraph:
            owloutput.add((supcls, RDF.type, OWL.Class))
            owloutput.add((measurementtype, RDFS.subClassOf, supcls))
            isSubclassedToDefaultSuperClass = False

    if isSubclassedToDefaultSuperClass:
        owloutput.add((measurementtype, RDFS.subClassOf, upperCollectionOntologyNs.SeaDataNetParameter))


outformat = 'turtle'
s = owloutput.serialize(format=outformat, encoding='utf-8').splitlines()
fout = open(datapath + collectionname + ".owl",'w',newline='\n')
# fout = open(collectionname + ".owl",'w',newline='\n')
for l in s:
    if l:
        # print(l.decode('utf-8'))
        fout.write(l.decode('utf-8'))
        fout.write('\n')

fout.close()

print('Saved ' + datapath + collectionname + ".owl" + " in " + outformat)
