import json
import urllib.request as req
import http.client as htclient
import codecs
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import RDF,RDFS,OWL,XSD,FOAF,DCTERMS
import re
import unicodedata
import collections



####### WKT Parser #######

Token = collections.namedtuple('Token', ['name','value'])
RuleMatch = collections.namedtuple('RuleMatch', ['name','matched'])

token_map = { '(':'LPAR', ')':'RPAR', ',':'COMMA', 'POINT':'POINT','LINESTRING':'LINESTRING', 'POLYGON':'POLYGON',
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

tokenizer = re.compile(token_regex_pattern, flags=re.IGNORECASE)
def parse_wkt(wkt):
##    print('parse_wkt', wkt)
    split_expr = tokenizer.findall(wkt)
    tokens = [Token(token_map.get(x, 'NUM'), x) for x in split_expr]    
    tree = match('geom', tokens)[0]
    return tree


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

def get_points_evaluate(tree):
    '''Credit to Erez at http://blog.erezsh.com/how-to-write-a-calculator-in-70-python-lines-by-writing-a-recursive-descent-parser/ '''
    solutions = _recurse_tree(tree,get_points_evaluate)
    return calc_map.get(tree.name, lambda x:x)(solutions)


get_geom_map = { 'geom' : lambda x: x,
                 'pointtag': lambda x: geosfNs.Point,
                 'linestringtag': lambda x: geosfNs.LineString,
                 'polygontag': lambda x: geosfNs.Polygon,
                 'multipointtag': lambda x: geosfNs.MultiPoint,
                 'multilinestringtag': lambda x: geosfNs.MultiLineString,
                 'multipolygontag': lambda x: geosfNs.MultiPolygon }

def get_geometry_evaluate(tree):
    solutions = _recurse_tree(tree,get_geometry_evaluate)
    return get_geom_map.get(tree.name, lambda x:x)(solutions)

### End WKT Parser #######




def unicode_to_ascii(text):
    table = {'&':'and'}
    for c in text:
        n = unicodedata.name(c[0][0])
        prog = re.compile(r"(CAPITAL|SMALL)\s+LETTER\s+(\w+)\s+\w+")
        result = prog.search(n)
        if result != None:
            table[c] = result.group(2)
            if result.group(1) == 'SMALL': table[c] = table[c].lower()

    return text.translate(str.maketrans(table))

featureNs = Namespace('http://data.geolink.org/id/feature/gebco/')
glview = Namespace('http://schema.geolink.org/dev/view#')
featuretypeNs = Namespace('http://schema.geolink.org/dev/voc/gebco/featuretype#')
geosparqlNs = Namespace('http://www.opengis.net/ont/geosparql#')
geosfNs = Namespace('http://www.opengis.net/ont/sf#')
geoNs = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
bibliotext = 'IHO-IOC GEBCO Gazetteer of Undersea Feature Names, www.gebco.net'

def run():
    gebcoURI = 'http://www.gebco.net/data_and_products/undersea_feature_names/'

    baseuri = 'http://www.ngdc.noaa.gov/gazetteer/rest/feature'
    requri = baseuri + '?max=5000'
    print('opening', requri, '...')
    response = req.urlopen(requri)
    print('opened')
    reader = codecs.getreader('utf-8')
    print('loading JSON raw data ...')
    jsondata = json.load(reader(response))
    print('loaded')

##    prettyprint = json.dumps(jsondata, sort_keys=True, indent=3, separators=(',',': '))
##    print(prettyprint)
    
    g = Graph()
    g.bind('rdf', RDF)
    g.bind('rdfs', RDFS)        
    g.bind('dcterms', DCTERMS)
    g.bind('glview', glview)
    g.bind('data_gebco', featureNs)
    g.bind('glvoc_gebco', featuretypeNs)        
    g.bind('geosparql', geosparqlNs)
    g.bind('geosf', geosfNs)

    print('populating',jsondata['totalCount'],'features to graph ... ')

    for feature in jsondata['items']:    
        feat_name = ' '.join(feature['name'].strip().split())
        feat_name_in_uri = feat_name.replace(' ', '_')
        if feature['type']:
            type_name = feature['type']['name'].strip()
        else:
            type_name = ''
        type_name_in_uri = type_name.replace(' ', '_').strip()
        feat_id = feature['id']
        
        label = ' '.join([feat_name,type_name]).strip()
        name_in_uri = '_'.join([feat_name_in_uri,type_name_in_uri, str(feat_id)])
        name_in_uri = unicode_to_ascii(name_in_uri)
        
        featureURI = featureNs[name_in_uri]
        if feature['type']:
            typeURI = featuretypeNs[type_name_in_uri]
        else:
            typeURI = glview.Feature
##        print(featureURI)        

        g.add( (featureURI, RDF.type, typeURI) )
        g.add( (featureURI, RDF.type, glview.Feature) )
        g.add( (featureURI, glview.hasFeatureType, typeURI) )
        g.add( (featureURI, RDFS.label, Literal(label)) )
        g.add( (featureURI, RDFS.seeAlso, URIRef(gebcoURI)) )
        g.add( (featureURI, DCTERMS.bibliographicCitation, Literal(bibliotext)) )
        jsonaddress = baseuri + '/' + str(feat_id)
        g.add( (featureURI, DCTERMS.isVersionOf, URIRef(jsonaddress)) )

        ## Note that we assume that all wktLiterals use the default coordinate reference system given by the URI:
        ## <http://www.opengis.net/def/crs/OGC/1.3/CRS84>,        
        ## The aforementioned URI denotes WGS84 longitude-latitude (Note that long value precedes the lat value)
        
        if feature['geometry']:
            geom = name_in_uri + '_geom1'
            geomURI = featureNs[geom]
            wkt = feature['geometry']
            wktparsetree = parse_wkt(wkt)
            geom = get_geometry_evaluate(wktparsetree)
            sftype = (list(geom))[0]            
            g.add( (featureURI, geosparqlNs.hasGeometry, geomURI) )
            g.add( (geomURI, RDF.type, sftype) )
            g.add( (geomURI, geosparqlNs.asWKT, Literal(wkt, datatype=geosparqlNs.wktLiteral)) )
        if feature['secondaryGeometry']:
            geom = name_in_uri + '_geom2'
            geomURI = featureNs[geom]
            wkt = feature['secondaryGeometry']
            wktparsetree = parse_wkt(wkt)
            geom = get_geometry_evaluate(wktparsetree)
            sftype = (list(geom))[0]            
            g.add( (featureURI, geosparqlNs.hasGeometry, geomURI) )
            g.add( (geomURI, RDF.type, sftype) )
            g.add( (geomURI, geosparqlNs.asWKT, Literal(wkt, datatype=geosparqlNs.wktLiteral)) )

##    print(g.serialize(format='turtle').decode(encoding='utf-8'))
    print('serializing to files..')
    foutname = 'features'
    with open(foutname+'.rdf', mode='w',encoding='utf-8') as rdffile:            
        print(g.serialize(format='xml').decode(), file=rdffile)
    print(foutname+'.rdf generated')
    with open(foutname+'.ttl', mode='w',encoding='utf-8') as rdffile:            
        print(g.serialize(format='turtle').decode(), file=rdffile)
    print(foutname+'.ttl generated')



if __name__ == '__main__':
    run()    
