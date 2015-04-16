from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import RDF,RDFS,OWL,XSD,FOAF,DCTERMS
from rdflib.plugins.stores.regexmatching import REGEXTerm
import re
import csv
import uuid
import sys

featureNs = Namespace('http://data.geolink.org/id/feature/gebco/')
glview = Namespace('http://schema.geolink.org/dev/view#')
featuretypeNs = Namespace('http://schema.geolink.org/dev/voc/gebco/featuretype#')
geosparqlNs = Namespace('http://www.opengis.net/ont/geosparql#')
geosfNs = Namespace('http://www.opengis.net/ont/sf#')

def getGeometry(wktText):
    types = {'multipoint':geosfNs.MultiPoint,
             'multilinestring':geosfNs.MultiLineString,
             'multipolygon':geosfNs.MultiPolygon,
             'geometrycollection':geosfNs.GeometryCollection,
             'point':geosfNs.Point,
             'linestring':geosfNs.LineString,
             'polygon':geosfNs.Polygon,
             'polyhedralsurface':geosfNs.PolyhedralSurface,
             'triangle':geosfNs.Triangle,
             'tin':geosfNs.TIN}
    for t in types:
        if wktText.lower().strip().startswith(t): return types[t]
    return None

def run(fname):
    g = Graph()
    with open(fname, newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        ## headers1 = [ str(c.encode(encoding='ascii', errors='xmlcharrefreplace')) for c in next(spamreader) ]
        headers = next(spamreader)
        dct = {}
        for h in headers:
            dct[h] = ''
        uridict = {}
        count = 0
        for row in spamreader:
            count += 1
            ## line = [ str(c.encode(encoding='ascii', errors='xmlcharrefreplace')) for c in row ]            
            for h,i in zip(headers, row):
                dct[h] = i
            label = dct['Specific Term'] + ' ' + dct['Generic Term']
            if label not in uridict: uridict[label] = 1
            else: uridict[label] += 1
            baseName = label.replace(' ', '_') + '_' + str(uridict[label])
            featureURI = featureNs[baseName]
            theClass = featuretypeNs[dct['Generic Term'].replace(' ', '_')]
            g.add( (featureURI, RDF.type, theClass) )
            g.add( (featureURI, RDF.type, glview.Feature) )
            g.add( (featureURI, glview.hasFeatureType, theClass) )
            g.add( (featureURI, RDFS.label, Literal(label)) )
            if dct['Origin of Name'] != '':
                g.add( (featureURI, DCTERMS.description, Literal(dct['Origin of Name'])) )
            if dct['Additional Information'] != '':
                g.add( (featureURI, DCTERMS.description, Literal(dct['Additional Information'])) )
            if dct['Coordinates'] != '':
                geom = baseName + '_geom1'
                geomURI = featureNs[geom]
                wkt = dct['Coordinates']
                g.add( (featureURI, geosparqlNs.hasGeometry, geomURI) )
                g.add( (geomURI, RDF.type, getGeometry(wkt)) )
                g.add( (geomURI, geosparqlNs.asWKT, Literal(wkt, datatype=geosparqlNs.wktLiteral)) )
            if dct['Secondary Coordinates'] != '':
                geom = baseName + '_geom2'
                geomURI = featureNs[geom]
                wkt = dct['Secondary Coordinates']
                g.add( (featureURI, geosparqlNs.hasGeometry, geomURI) )
                g.add( (geomURI, RDF.type, getGeometry(wkt)) )
                g.add( (geomURI, geosparqlNs.asWKT, Literal(wkt, datatype=geosparqlNs.wktLiteral)) )       
##            print(featureURI)
##            print('Origin of Name:', dct['Origin of Name'])
##            print('Additional Information:', dct['Additional Information'])
##            print()
##            if stop: break
        g.bind('rdf', RDF)
        g.bind('rdfs', RDFS)        
        g.bind('dcterms', DCTERMS)
        g.bind('glview', glview)
        g.bind('data_gebco', featureNs)
        g.bind('glvoc_gebco', featuretypeNs)        
        g.bind('geosparql', geosparqlNs)
        g.bind('geosf', geosfNs)
        print (len(g))
        print(count)
        foutname = fname[:fname.rfind('.')]
        with open(foutname+'.rdf', mode='w',encoding='utf-8') as rdffile:            
            print(g.serialize(format='xml').decode(), file=rdffile)
        print(foutname+'.rdf generated')
        with open(foutname+'.ttl', mode='w',encoding='utf-8') as rdffile:            
            print(g.serialize(format='turtle').decode(), file=rdffile)
        print(foutname+'.ttl generated')
       
if __name__ == '__main__':
    finput = 'features.csv'    
    run(finput)    
