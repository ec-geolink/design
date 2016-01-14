from rdflib import Graph, OWL, URIRef, RDF, RDFS, Literal, Namespace, BNode
from rdflib.namespace import SKOS, DC, DCTERMS

datapath = "./"
collectionname = "P03"
graphURIString = datapath + collectionname + "-source.rdf"
g = Graph()
result = g.parse(graphURIString)

print(graphURIString, "has %s statements." % len(g))

# s = g.serialize(format='turtle').splitlines()
# for l in s:
#     if l: print(l.decode('utf-8'))

## write as OWL
idschemeOntoNs = Namespace("http://schema.geolink.org/1.0/voc/identifierscheme#")
ontologyURIString = "http://schema.geolink.org/1.0/voc/nvs/" + collectionname
defaultNS = Namespace(ontologyURIString + '#')
glbaseNS = Namespace('http://schema.geolink.org/1.0/base/main#')
comment = "This ontology captures SeaDataNet Agreed Parameter Groups from the NERC vocabulary server"
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

## adding object property glbase:hasMeasurementType, glbase:hasIdentifier,
## glbase:hasIdentifierScheme, glbase:hasIdentifierValue
owloutput.add((glbaseNS.hasMeasurementType, RDF.type, OWL.ObjectProperty))
owloutput.add((glbaseNS.hasIdentifier, RDF.type, OWL.ObjectProperty))
owloutput.add((glbaseNS.hasIdentifierScheme, RDF.type, OWL.ObjectProperty))
owloutput.add((glbaseNS.hasIdentifierValue, RDF.type, OWL.DatatypeProperty))

## adding class :SeaDataNetParameter, glbase:MeasurementType
owloutput.add((defaultNS.SeaDataNetParameter, RDF.type, OWL.Class))
owloutput.add((glbaseNS.MeasurementType, RDF.type, OWL.Class))


## add each member of the P03 collection, i.e., Measurement types to ontology as instances of MeasurementType
## and pun them as OWL Classes too;
colcreator = g.value(collectionURI, DCTERMS.creator, None)
for measurementtype in g.objects(collectionURI, SKOS.member):
    owloutput.add((measurementtype, RDF.type, OWL.NamedIndividual))
    owloutput.add((measurementtype, RDF.type, OWL.Class))
    owloutput.add((measurementtype, RDF.type, glbaseNS.MeasurementType))

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
    ## we assume idschemeOntoNs.sdnp03 as the identifier scheme for the measurement types (SeaDataNet P03)
    ## the identifier scheme is assumed to already be defined in identifierscheme.owl
    owloutput.add((bn, glbaseNS.hasIdentifierScheme, idschemeOntoNs.sdnp03))

    ## get equivclass
    for equivcls in g.objects(measurementtype, OWL.sameAs):
        if (collectionURI, SKOS.member, equivcls) in  g:
            owloutput.add(collectionURI, OWL.equivalentClass, equivcls)

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

    if isSubclassedToDefaultSuperClass:
        owloutput.add((measurementtype, RDFS.subClassOf, defaultNS.SeaDataNetParameter))


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
