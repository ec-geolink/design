from rdflib import Graph, OWL, URIRef, RDF, RDFS, Literal, Namespace, BNode
from rdflib.namespace import SKOS, DC, DCTERMS

datapath = "/Users/krisnadhi/github.com/ec-geolink/design/voc/nvs/"
collectionname = "L06"
graphURIString = datapath + collectionname + "-source.rdf"
g = Graph()
result = g.parse(graphURIString)

print(graphURIString, "has %s statements." % len(g))

s = g.serialize(format='turtle').splitlines()
for l in s:
    if l: print(l.decode('ascii'))

## write as OWL
idschemeOntoNs = Namespace("http://schema.geolink.org/1.0/voc/identifierscheme#")
ontologyURIString = "http://schema.geolink.org/1.0/voc/nvs/" + collectionname
DefaultNS = Namespace(ontologyURIString + '#')
GLBaseNS = Namespace('http://schema.geolink.org/1.0/base/main#')
comment = "This ontology captures SeaVoX platform categories (e.g., vessel, mooring, etc.) as hosted in the NERC vocabulary server"
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

## adding object property glbase:hasPlatformType, glbase:hasIdentifier,
## glbase:hasIdentifierScheme, glbase:hasIdentifierValue
owloutput.add((GLBaseNS.hasPlatformType, RDF.type, OWL.ObjectProperty))
owloutput.add((GLBaseNS.hasIdentifier, RDF.type, OWL.ObjectProperty))
owloutput.add((GLBaseNS.hasIdentifierScheme, RDF.type, OWL.ObjectProperty))
owloutput.add((GLBaseNS.hasIdentifierValue, RDF.type, OWL.DatatypeProperty))

## adding class glbase:Platform, glbase:PlatformType
owloutput.add((GLBaseNS.Platform, RDF.type, OWL.Class))
owloutput.add((GLBaseNS.PlatformType, RDF.type, OWL.Class))


## add each member of the L06 collection, i.e., platform types to ontology as instances of PlatformType
## and pun them as OWL Classes too;
colcreator = g.value(collectionURI, DCTERMS.creator, None)
for platformtype in g.objects(collectionURI, SKOS.member):
    owloutput.add((platformtype, RDF.type, OWL.NamedIndividual))
    owloutput.add((platformtype, RDF.type, OWL.Class))
    owloutput.add((platformtype, RDF.type, GLBaseNS.PlatformType))

    ## add typecasting axiom
    bn1 = BNode()
    bn2 = BNode()
    lst = BNode()
    owloutput.add((bn1, RDF.type, OWL.Restriction))
    owloutput.add((bn1, OWL.onProperty, GLBaseNS.hasPlatformType))
    owloutput.add((bn1, OWL.someValuesFrom, bn2))
    owloutput.add((bn2, RDF.type, OWL.Class))
    owloutput.add((bn2, OWL.oneOf, lst))
    owloutput.add((lst, RDF.first, platformtype))
    owloutput.add((lst, RDF.rest, RDF.nil))
    owloutput.add((bn1, RDFS.subClassOf, platformtype))

    label = g.value(platformtype, SKOS.prefLabel, None)
    owloutput.add((platformtype, RDFS.label, label)) # add the pref-label as rdfs:label in the ontology
    definition = g.value(platformtype, SKOS.definition, None)
    owloutput.add((platformtype, RDFS.comment, definition)) # add skos definition as rdfs:comment in the onto
    date = g.value(platformtype, DCTERMS.date, None)
    owloutput.add((platformtype, DCTERMS.date, date)) # add original definition date of platformtype to onto
    owloutput.add((platformtype, DCTERMS.creator, colcreator))
    # add identifier
    bn = BNode()
    ident = g.value(platformtype, DCTERMS.identifier, None)
    owloutput.add((platformtype, GLBaseNS.hasIdentifier, bn))
    owloutput.add((bn, GLBaseNS.hasIdentifierValue, ident))
    ## we assume idschemeOntoNs.sdnl06 as the identifier scheme for the platform types (SeaDataNet L06)
    ## the identifier scheme is assumed to already be defined in identifierscheme.owl
    owloutput.add((bn, GLBaseNS.hasIdentifierScheme, idschemeOntoNs.sdnl06))

    ## get subclass
    for subcls in g.objects(platformtype, SKOS.narrower):
        if (collectionURI, SKOS.member, subcls) in g:
            owloutput.add((subcls, RDFS.subClassOf, platformtype))
    ## get superclass
    isDirectSubClassofPlatform = True
    for supcls in g.objects(platformtype, SKOS.broader):
        if (collectionURI, SKOS.member, supcls) in g:
            owloutput.add((platformtype, RDFS.subClassOf, supcls))
            isDirectSubClassofPlatform = False

    if isDirectSubClassofPlatform:
        owloutput.add((platformtype, RDFS.subClassOf, GLBaseNS.Platform))


s = owloutput.serialize(format='pretty-xml').splitlines()
fout = open(datapath + collectionname + ".owl",'w',newline='\n')
#fout = open("l06.owl",'w',newline='\n')
for l in s:
    if l:
        print(l.decode('utf-8'))
        fout.write(l.decode('utf-8'))
        fout.write('\n')

fout.close()










