from rdflib import Graph, OWL, URIRef, RDF, RDFS, Literal, Namespace, BNode
from rdflib.namespace import SKOS, DC, DCTERMS

datapath = "./"
collectionname = "L05"
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
DefaultNS = Namespace(ontologyURIString + '#')
GLBaseNS = Namespace('http://schema.geolink.org/1.0/base/main#')
comment = "This ontology captures SeaDataNet device categories from the NERC vocabulary server"
ontologyCreator = "EarthCube GeoLink project"
owloutput = Graph()
owloutput.bind('', DefaultNS)
owloutput.bind('glbase', GLBaseNS)
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

## adding object property glbase:hasInstrumentType, glbase:hasIdentifier,
## glbase:hasIdentifierScheme, glbase:hasIdentifierValue
owloutput.add((GLBaseNS.hasInstrumentType, RDF.type, OWL.ObjectProperty))
owloutput.add((GLBaseNS.hasIdentifier, RDF.type, OWL.ObjectProperty))
owloutput.add((GLBaseNS.hasIdentifierScheme, RDF.type, OWL.ObjectProperty))
owloutput.add((GLBaseNS.hasIdentifierValue, RDF.type, OWL.DatatypeProperty))

## adding class glbase:Instrument, glbase:InstrumentType
owloutput.add((GLBaseNS.Instrument, RDF.type, OWL.Class))
owloutput.add((GLBaseNS.InstrumentType, RDF.type, OWL.Class))


## add each member of the L05 collection, i.e., Instrument types to ontology as instances of InstrumentType
## and pun them as OWL Classes too;
colcreator = g.value(collectionURI, DCTERMS.creator, None)
for instrumenttype in g.objects(collectionURI, SKOS.member):
    owloutput.add((instrumenttype, RDF.type, OWL.NamedIndividual))
    owloutput.add((instrumenttype, RDF.type, OWL.Class))
    owloutput.add((instrumenttype, RDF.type, GLBaseNS.InstrumentType))

    ## add typecasting axiom
    bn1 = BNode()
    bn2 = BNode()
    lst = BNode()
    owloutput.add((bn1, RDF.type, OWL.Restriction))
    owloutput.add((bn1, OWL.onProperty, GLBaseNS.hasInstrumentType))
    owloutput.add((bn1, OWL.someValuesFrom, bn2))
    owloutput.add((bn2, RDF.type, OWL.Class))
    owloutput.add((bn2, OWL.oneOf, lst))
    owloutput.add((lst, RDF.first, instrumenttype))
    owloutput.add((lst, RDF.rest, RDF.nil))
    owloutput.add((bn1, RDFS.subClassOf, instrumenttype))

    label = g.value(instrumenttype, SKOS.prefLabel, None)
    owloutput.add((instrumenttype, RDFS.label, label)) # add the pref-label as rdfs:label in the ontology
    definition = g.value(instrumenttype, SKOS.definition, None)
    owloutput.add((instrumenttype, RDFS.comment, definition)) # add skos definition as rdfs:comment in the onto
    date = g.value(instrumenttype, DCTERMS.date, None)
    owloutput.add((instrumenttype, DCTERMS.date, date)) # add original definition date of instrumenttype to onto
    owloutput.add((instrumenttype, DCTERMS.creator, colcreator))
    # add identifier
    bn = BNode()
    ident = g.value(instrumenttype, DCTERMS.identifier, None)
    owloutput.add((instrumenttype, GLBaseNS.hasIdentifier, bn))
    owloutput.add((bn, GLBaseNS.hasIdentifierValue, ident))
    ## we assume idschemeOntoNs.sdnl05 as the identifier scheme for the instrument types (SeaDataNet L05)
    ## the identifier scheme is assumed to already be defined in identifierscheme.owl
    owloutput.add((bn, GLBaseNS.hasIdentifierScheme, idschemeOntoNs.sdnl05))

    ## get equivclass
    for equivcls in g.objects(instrumenttype, OWL.sameAs):
        if (collectionURI, SKOS.member, equivcls) in  g:
            owloutput.add(collectionURI, OWL.equivalentClass, equivcls)

    ## get subclass
    for subcls in g.objects(instrumenttype, SKOS.narrower):
        if (collectionURI, SKOS.member, subcls) in g:
            owloutput.add((subcls, RDFS.subClassOf, instrumenttype))
    ## get superclass
    isDirectSubClassofInstrument = True
    for supcls in g.objects(instrumenttype, SKOS.broader):
        if (collectionURI, SKOS.member, supcls) in g:
            owloutput.add((instrumenttype, RDFS.subClassOf, supcls))
            isDirectSubClassofInstrument = False

    if isDirectSubClassofInstrument:
        owloutput.add((instrumenttype, RDFS.subClassOf, GLBaseNS.Instrument))


s = owloutput.serialize(format='pretty-xml').splitlines()
fout = open(datapath + collectionname + ".owl",'w',newline='\n')
# fout = open(collectionname + ".owl",'w',newline='\n')
for l in s:
    if l:
        # print(l.decode('utf-8'))
        fout.write(l.decode('utf-8'))
        fout.write('\n')

fout.close()










