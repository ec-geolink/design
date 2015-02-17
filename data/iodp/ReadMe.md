# Notes on Janus and CHRONOS samples with a goal of implementing the GeoLink sample pattern


> There are two sections here.  One Janus (on the IODP Janus data) and one for CHRONOS on the related (but different) CHRONOS sample (and taxon occurrence) data.  


## Janus
All SPARQL calls are against http://data.oceandrilling.org/sparql unless otherwise noted.  

### Notes:
1. Janus database is currently offline, so ETL from the original source is something I need to rebuild.  I have all the parts for setting up my own copy from TAMU and will be doing that soon.
2. An old graph made from the Janus DB exist and I am doing SPARQL constructs off that.  I will likely rebuild the graph from the source when it is back on-line so I can do some QA QC tests

To look at what I have in terms of items in a Janus sample use this simple SPARQL that just show some of what I associate with a sample now is:

```sparql
# sparql call for a janus sample
PREFIX iodp: <http://data.oceandrilling.org/core/1/>
SELECT DISTINCT  ?p ?o
FROM <http://data.oceandrilling.org/janus/>
WHERE {
   <http://data.oceandrilling.org/janus/parameter/sampleCount/207/1259/3727> ?p ?o .
}
```

So I could look at making a CONSTRUCT call like:

Note:  I am stilling trying to figure out how to implement the pattern in a CONSTRUCT call, so notes, edits and comments are welcome.  

Note:  I did a limit 1 here just to limit the results.  One can alter that to increase the results.  There are a LOT of samples, so removing limit is not wise.  If the time comes to build out all the items then I will do that local to the machine using the Virtuoso command line isql call.  Over the web UI it is guaranteed to time out.   

```sparql
PREFIX glfoo: <http://glfoo.org/>
PREFIX iodp: <http://data.oceandrilling.org/core/1/>
PREFIX qb:  <http://purl.org/linked-data/cube#>
PREFIX janus: <http://data.oceandrilling.org/janus/>
PREFIX sdmx-dimension:  <http://purl.org/linked-data/sdmx/2009/dimension#>
CONSTRUCT {
     ?s a glfoo:PhysicalSample .
     ?s glfoo:hasOrginalSampleProduction _:osp .
     _:osp glfoo:hasCruise ?expuri .
     _:osp glfoo:hasDepth ?depth .
     _:osp glfoo:hasPlace ?location .
     _:osp glfoo:hasTime ?time .
     ?s glfoo:isDescribedBy _:sio .
     _:sio glfoo:hasRelatedSampleID ?sampleid 
} 
FROM  NAMED <http://data.oceandrilling.org/janus/>
FROM  NAMED <http://data.oceandrilling.org/codices#>
 WHERE {
 	GRAPH <http://data.oceandrilling.org/janus/> {
        ?s janus:parameter <http://data.oceandrilling.org/core/1/janus/sampleCount> .
        ?s janus:leg ?leg .
        ?s janus:site ?site .
        ?s janus:hole ?hole .
        ?s janus:core ?core .
        ?s janus:sectionnumber ?sectionnumber .
        ?s janus:sampleid ?sampleid .
        ?s janus:getdepthsxsectionidstdstopinterval00 ?depth .
        ?s janus:location ?location .
        ?s janus:tocharstimestampmmddyyyyhh24mi  ?time
    }
    GRAPH <http://data.oceandrilling.org/codices#> {
    	?uri iodp:expedition "113" .
   		?uri skos:broader ?uri2 .
   		?uri2 skos:broader ?expuri
    }
}
LIMIT 1
```





## CHRONOS

CHRONOS data is derived from the Janus data.   It is different, but closely related and will make a good exercise of the linked data principles. 

There are two main items I can extract from the relational database and represent in graphs for the CHRONOS data.  These are taxon occurrence (finding a bug) and sample id, the actual sample the bug(s) were found in.

A taxon occurrence might look like:

```sparql
<http://chronos.org/id/chronos/sample/v1/e0c2cc85-b6c2-11e4-8ea0-d49a20be82c0> a chronos:taxonoccurrence ;
        chronos:sampleid "42470" ;
        ocd:leg "152" ;
        ocd:site "918" ;
        ocd:hole "A" ;
        chronos:hole_id "152_918A" ;
        chronos:taxon_abundance "R" ;
        chronos:taxon "Coccolithus pelagicus" ;
        chronos:fossil_group "N" ;
        chronos:water_depth "1869" ;
        chronos:sample_age_ma "-0.306221" ;
        chronos:sample_depth_mbsf "2.10" ;
        geo:lat  63.0928 ;
        geo:long  -38.6389 .
```

A sample might look like:

```sparql
<http://chronos.org/id/chronos/sample/v1/e77ea2b0-b6c2-11e4-8579-d49a20be82c0> a chronos:sample ;
        chronos:sampleid "42470" ;
        ocd:leg "152" ;
        ocd:site "918" ;
        ocd:hole "A" ;
        chronos:ocean_code "ATL" ;
        chronos:water_depth "1869" ;
        chronos:sample_age_ma "-0.306221" ;
        chronos:sample_depth_mbsf "2.10" ;
        geo:lat  63.0928 ;
        geo:long  -38.6389 .
```

Note:  The CHRONOS sampleid is not the Janus sampleid.  However we should be able to connect the two given the data we have.  

These graphs are built from a simple Go based ETL code reading the PostgreSQL database.  So it will be easy to implement creating a graph based on the GeoLink Sample pattern once I grok how to do so.  

Goal:  Understand how to build these out in GeoLink and encode that in the Go code and rebuild.  Once that is done those will be ready to publish graphs.  