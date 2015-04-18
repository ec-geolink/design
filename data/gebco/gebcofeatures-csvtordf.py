from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import RDF,RDFS,OWL,XSD,FOAF,DCTERMS
from rdflib.plugins.stores.regexmatching import REGEXTerm
import re
import csv
import uuid
import unicodedata
import collections
import itertools


featureNs = Namespace('http://data.geolink.org/id/feature/gebco/')
glview = Namespace('http://schema.geolink.org/dev/view#')
featuretypeNs = Namespace('http://schema.geolink.org/dev/voc/gebco/featuretype#')
geosparqlNs = Namespace('http://www.opengis.net/ont/geosparql#')
geosfNs = Namespace('http://www.opengis.net/ont/sf#')

def unicode_to_ascii(text):
    table = {}
    for c in text:
        n = unicodedata.name(c[0][0])
        prog = re.compile(r"(CAPITAL|SMALL)\s+LETTER\s+(\w+)\s+\w+")
        result = prog.search(n)
        if result != None:
            table[c] = result.group(2)
            if result.group(1) == 'SMALL': table[c] = table[c].lower()

    return text.translate(str.maketrans(table))

def getGeometry(wktText):
    ## This may not work if the wktText is preceded with the URI of a coordinate reference system (CRS)    
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
    endCRSURIpos = wktText.find('>')
    if endCRSURIpos > -1: wktText = wktText[:endCRSURI+1]
    wktText = wktText.strip().lower()
    for t in types:
        if wktText.startswith(t): return types[t]
    return None

geomtypes = {'multipoint':0, 'multilinestring':0, 'multipolygon':0,
         'geometrycollection':0, 'point':0, 'linestring':0, 'polygon':0,
         'polyhedralsurface':0, 'triangle':0, 'tin':0}

Token = collections.namedtuple('Token', ['name','value'])
RuleMatch = collections.namedtuple('RuleMatch', ['name','matched'])

## limited wkt grammar
## atom : NUM
## geom : point 
## point: POINT LPAR atom atom RPAR
## points : point | point COMMA points
## linestring : LINESTRING LPAR points RPAR

token_map = { '(':'LPAR', ')':'RPAR', ',':'COMMA', 'POINT':'POINT',
            'LINESTRING':'LINESTRING', 'POLYGON':'POLYGON',
            'MULTIPOINT':'MULTIPOINT','MULTILINESTRING':'MULTILINESTRING', 'MULTIPOLYGON':'MULTIPOLYGON'}
signed_exact_num_pattern = '[-+]?\d*\.?\d+'
signed_approx_num_pattern = signed_exact_num_pattern + 'E[-+]?\d*'
escape = (lambda x : '\\'+x if x == '(' or x == ')' else x)
token_regex_pattern = '|'.join([signed_exact_num_pattern, signed_approx_num_pattern]) +'|' + '|'.join(map(escape,token_map))

rule_map = { 'atom'          : ['NUM'],
             'pair'          : ['atom atom'],
             'pairs'         : ['pair COMMA pairs', 'pair'],
             'geom'          : ['pointtag', 'linestringtag', 'polygontag','multipointtag','multilinestringtag','multipolygontag'],
             'pointtag'      : ['POINT point'],
             'point'         : ['LPAR pair RPAR'],
             'points'        : ['point COMMA points', 'point'],
             'linestringtag' : ['LINESTRING linestring'],
             'linestring'    : ['LPAR pairs RPAR'],
             'linestrings'   : ['linestring COMMA linestrings', 'linestring'],
             'polygontag'    : ['POLYGON polygon'],
             'polygon'       : ['LPAR linestrings RPAR'],
             'polygons'      : ['polygon COMMA polygons', 'polygon'],
             'multipointtag' : ['MULTIPOINT multipoint'],
             'multipoint'    : ['LPAR points RPAR'],
             'multilinestringtag' : ['MULTILINESTRING multilinestring'],
             'multilinestring' : ['LPAR linestrings RPAR'],
             'multipolygontag' : ['MULTIPOLYGON multipolygon'],
             'multipolygon' : ['LPAR polygons RPAR']
             }

    
calc_map = { 'NUM' : float,
             'atom' : lambda x : (list(x))[0],
             'pair' : lambda x : tuple(x),
             'pairs' : lambda x : (lambda y : y if len(y)<=1 else [y[0]]+y[2])(list(x)),
             'geom' : lambda x : (list(x))[0],
             'pointtag' : lambda x : (list(x))[1],
             'point' : lambda x : [(list(x))[1]],
             'points' : lambda x : (lambda y : y if len(y)<=1 else [y[0]]+y[2])(list(x)),
             'linestringtag' : lambda x : (list(x))[1],
             'linestring' : lambda x : (list(x))[1],
             'linestrings' : lambda x : (lambda y : y if len(y)<=1 else [y[0]]+y[2])(list(x)),
             'polygontag' : lambda x : (list(x))[1],
             'polygon' : lambda x : (list(x))[1],
             'polygons' : lambda x : (lambda y : y if len(y)<=1 else [y[0]]+y[2])(list(x)),
             'multipointtag' : lambda x : (list(x))[1],
             'multipoint' : lambda x : (list(x))[1],             
             'multilinestringtag': lambda x : (list(x))[1],
             'multilinestring' : lambda x : (list(x))[1],
             'multipolygontag': lambda x : (list(x))[1],
             'multipolygon' : lambda x : (list(x))[1]} 

def match(rule_name, tokens):
    '''Credit to Erez at http://blog.erezsh.com/how-to-write-a-calculator-in-70-python-lines-by-writing-a-recursive-descent-parser/ '''
    if tokens and rule_name == tokens[0].name:      # Match a token?
        return RuleMatch(tokens[0], tokens[1:])
    for expansion in rule_map.get(rule_name, ()):   # Match a rule?
        remaining_tokens = tokens
        matched_subrules = []
        for subrule in expansion.split():
            matched, remaining_tokens = match(subrule, remaining_tokens)
            if not matched:
                break   # no such luck. next expansion!
            matched_subrules.append(matched)
        else:
            return RuleMatch(rule_name, matched_subrules), remaining_tokens
    return None, None   # match not found

def _recurse_tree(tree,func):
    '''Credit to Erez at http://blog.erezsh.com/how-to-write-a-calculator-in-70-python-lines-by-writing-a-recursive-descent-parser/ '''
    return map(func, tree.matched) if tree.name in rule_map else tree[1]

def evaluate(tree):
    '''Credit to Erez at http://blog.erezsh.com/how-to-write-a-calculator-in-70-python-lines-by-writing-a-recursive-descent-parser/ '''
    solutions = _recurse_tree(tree,evaluate)
##    print('eval', tree.name, list(solutions), str(solutions), calc_map.get(tree.name, lambda x:x))
    return calc_map.get(tree.name, lambda x:x)(solutions)

tokenizer = re.compile(token_regex_pattern, flags=re.IGNORECASE)
def getPoints(expr):
    split_expr = tokenizer.findall(expr)
    tokens = [Token(token_map.get(x, 'NUM'), x) for x in split_expr]    
    tree = match('geom', tokens)[0]
##    print(tokens)
##    print(tree)    
    sol = evaluate(tree)
    return sol

def getCentroid(wktText):    
    if wktText.strip() == '': return RuntimeError

    wkt = wktText
##    if (not wkt.startswith('POINT')) and (not wkt.startswith('LINESTRING')) and (not wkt.startswith('POLYGON')):
##        print(wkt) 
    points = getPoints(wkt)
##    if (not wkt.startswith('POINT')) and (not wkt.startswith('LINESTRING')) and (not wkt.startswith('POLYGON')):
##        print(points)
    points = flatten(points)
    acc = itertools.accumulate(points, lambda p,q : (p[0] + q[0], p[1]+q[1]))
    sumpoint = list(acc)[-1]
    centroid = (sumpoint[0]/len(points), sumpoint[1]/len(points))
##    print(points, centroid)
    return centroid


def flatten(xs):
    if xs == [] or isinstance(xs[0],tuple):
        return xs
    else:
        return flatten(xs[0]) + flatten(xs[1:])
        
    

gebcoURI = 'http://www.gebco.net/data_and_products/undersea_feature_names/'

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
            baseName = label.replace(' ', '_') ##+ '_' + str(uridict[label])            
            
            centroid = getCentroid(dct['Coordinates'])
            print(label, centroid, centroid.__class__.__name__)
            
            xx = str(round(centroid[0],2))
            yy = str(round(centroid[1],2))
            baseName = unicode_to_ascii(baseName) + '_' + xx.replace('.','_') + '_' + yy.replace('.','_')
            print(baseName)
            featureURI = featureNs[baseName]
            theClass = featuretypeNs[dct['Generic Term'].replace(' ', '_')]
            g.add( (featureURI, RDF.type, theClass) )
            g.add( (featureURI, RDF.type, glview.Feature) )
            g.add( (featureURI, glview.hasFeatureType, theClass) )
            g.add( (featureURI, RDFS.label, Literal(label)) )
            g.add( (featureURI, RDFS.seeAlso, URIRef(gebcoURI)) )
##            if dct['Origin of Name'] != '':
##                g.add( (featureURI, DCTERMS.description, Literal(dct['Origin of Name'])) )
##            if dct['Additional Information'] != '':
##                g.add( (featureURI, DCTERMS.description, Literal(dct['Additional Information'])) )
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
        print(geomtypes)
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
