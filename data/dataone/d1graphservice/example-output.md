# Example Output from D1 Graph Service

To show what comes out of the graph service, I'd like to show the inputs and
what the resulting output (RDF) is.

Given a dataset with PID:

```
doi:10.5063/AA/nceas.920.2
```

which has the system metadata:

```{xml}
<d1:systemMetadata xmlns:d1="http://ns.dataone.org/service/types/v1">
  <serialVersion>12</serialVersion>
  <identifier>doi:10.5063/AA/nceas.920.2</identifier>
  <formatId>eml://ecoinformatics.org/eml-2.0.1</formatId>
  <size>7736</size>
  <checksum algorithm="MD5">2bdef8316498220cf2f625f288169a40</checksum>
  <submitter>uid=nceasadmin,o=NCEAS,dc=ecoinformatics,dc=org</submitter>
  <rightsHolder>uid=nceasadmin,o=NCEAS,dc=ecoinformatics,dc=org</rightsHolder>
  <accessPolicy>
    <allow>
      <subject>uid=nceasadmin,o=NCEAS,dc=ecoinformatics,dc=org</subject>
      <permission>read</permission>
      <permission>write</permission>
      <permission>changePermission</permission>
    </allow>
    <allow>
      <subject>uid=nceasadmin,o=NCEAS,dc=ecoinformatics,dc=org</subject>
      <permission>read</permission>
      <permission>write</permission>
      <permission>changePermission</permission>
    </allow>
    <allow>
      <subject>public</subject>
      <permission>read</permission>
    </allow>
  </accessPolicy>
  <replicationPolicy numberReplicas="2" replicationAllowed="true">
    <preferredMemberNode/>
    <blockedMemberNode/>
  </replicationPolicy>
  <obsoletes>doi:10.5063/AA/nceas.920.1</obsoletes>
  <archived>false</archived>
  <dateUploaded>2008-04-09T23:00:00.000+00:00</dateUploaded>
  <dateSysMetadataModified>2015-01-06T06:06:24.872+00:00</dateSysMetadataModified>
  <originMemberNode>urn:node:KNB</originMemberNode>
  <authoritativeMemberNode>urn:node:KNB</authoritativeMemberNode>
  <replica>
    <replicaMemberNode>urn:node:CN</replicaMemberNode>
    <replicationStatus>completed</replicationStatus>
    <replicaVerified>2015-01-06T04:45:49.623+00:00</replicaVerified>
  </replica>
  <replica>
    <replicaMemberNode>urn:node:mnUCSB1</replicaMemberNode>
    <replicationStatus>completed</replicationStatus>
    <replicaVerified>2015-01-06T06:06:06.196+00:00</replicaVerified>
  </replica>
  <replica>
    <replicaMemberNode>urn:node:mnORC1</replicaMemberNode>
    <replicationStatus>completed</replicationStatus>
    <replicaVerified>2015-01-06T06:06:15.311+00:00</replicaVerified>
  </replica>
  <replica>
    <replicaMemberNode>urn:node:KNB</replicaMemberNode>
    <replicationStatus>completed</replicationStatus>
    <replicaVerified>2015-01-06T06:06:23.455+00:00</replicaVerified>
  </replica>
</d1:systemMetadata>
```

And the science metadata:

```{xml}
<eml:eml packageId="nceas.920.2" scope="system" system="knb" xmlns:ds="eml://ecoinformatics.org/dataset-2.0.1" xmlns:eml="eml://ecoinformatics.org/eml-2.0.1" xmlns:stmml="http://www.xml-cml.org/schema/stmml"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="eml://ecoinformatics.org/eml-2.0.1 eml.xsd">
  <dataset scope="document">
    <title>
      The Ecology and Conservation of Asian Hornbills Book
    </title>
    <creator id="1207779657828" scope="document">
      <organizationName>
        NCEAS 6140: Kinnaird: Functional relationships of Asian Hornbills in changing forest landscapes
      </organizationName>
    </creator>
    <creator id="1207779666443" scope="document">
      <individualName>
        <givenName>Timothy G.</givenName>
        <surName>O'Brien</surName>
      </individualName>
      <electronicMailAddress>tobrian@wcs.org</electronicMailAddress>
    </creator>
    <creator id="1207779657902" scope="document">
      <organizationName>
        National Center for Ecological Analysis and Synthesis
      </organizationName>
    </creator>
    <creator id="1207779657950" scope="document">
      <individualName>
        <givenName>Margaret F.</givenName>
        <surName>Kinnaird</surName>
      </individualName>
      <electronicMailAddress>mkinnaird@wcs.org</electronicMailAddress>
    </creator>
    <metadataProvider scope="document">
      <individualName>
        <givenName>Callie</givenName>
        <surName>Bowdish</surName>
      </individualName>
    </metadataProvider>
    <pubDate>2008-04-09</pubDate>
    <abstract>
      <para>
        This book contains a number of data tables regarding Asian Hornbills and their relationship to the Asian ecosystem. The tables included in this publication are titled: 1.1 Scientific and Common names for 31 species (including subspecies) within their
        distribution and habitats; 2.1 Forty years of shifting hornbill taxonomy; 2.2 Mean wing and body size for samples of male and female Asian Hornbills; 2.3 Results of principal components analysis of degree of sexual dimorphism and generic-level
        differences; 2.5 Morphological differences and occurrence of territoriality among Asian hornbills; 3.1 Rainfall seasonality across the hornbill realm for 61 sites in 12 countries; 3.2 Summary of selected phenological studies in Asia; 4.1 Comparison
        of fruit and animal matter in the diets of 17 species of Asian hornbills during breeding and nonbreeding seasons; 4.2 Number of genera and species in 46 families of fruiting plants identified in the diets of 17 species of well-studied Asian
        hornbills; 4.3 Dietary diversity reported in 26 studies of 16 Asian hornbill species; 4.4 Diet overlap for 43 hornbill species pairs from 7 locations; 4.5 Description of vegetation plots used for estimating fruit availability in Tankoko, Sulawesi,
        and BBSNP Sumatra; 4.6 Estimates of monthly fruit availability in Tangkoko, Sulawesi, and BBSNP, Sumatra; 4.7 Estimates of hornbill biomass for Tangkoko and BBSNP study sites; 5.1 Nesting season in reltion to the onset of rain for 22 species of Asian
        hornbills by country and position relative to equator; 5.2 Measures of fruit availability during courtship, nesting, and fledging periods; 5.4 Nest characteristics for 14 hornbill species studied at 8 forest sites; 5.4 Maximum clutch size and egg
        volume for 26 hornbill species; 5.5 Breeding parameters for 22 hornbill species; 6.1 Nesting success in four orders of birds; 6.2 Cooperatively breeding hornbills within the family Bucerotidae; 7.1 Movement patterns of six adult male Red-knobbed
        Hornbills and two Sulawesi Tarictic Hornbill families; 7.2 Description of four hornbill diet tree species used for modeling ecologically functional populations; 7.3 Size-class distributions and probabilities of survivial (l%26#226;%26#130;%26#147;)
        and mortality (m%26#226;%26#130;%26#147;) for four hornbill diet species used to model ecologically functional hornbill populations; 7.4 Dispersal and germination of four species of hornbill diet trees; 8.1 Human population statistics and forest area
        in the hornbill realm; 8.2 Conservation status of 31 species of Asian hornbills based on the IUCN Red List of Threatened Species; 8.3 Measures of current range size and habitat configuration for Asian hornbills; 8.4 Characteristics of hornbill
        neighborhoods; 8.5 Suggested changes in the IUCN Red List of Threatened Species categories of 31 species of Asian hornbills; 9.1 Range, IUCN protected areas, and proportion of suitable habitat in those area for 31 Asian hornbill species.
      </para>
    </abstract>
    <keywordSet>
      <keyword>ecology</keyword>
      <keyword>hornbill</keyword>
      <keyword>conservation</keyword>
      <keyword>tropical Asia</keyword>
      <keyword>Asian Forest</keyword>
      <keyword>Asian Hornbills</keyword>
      <keyword>keystone</keyword>
      <keywordThesaurus>None</keywordThesaurus>
    </keywordSet>
    <additionalInfo>
      <para>
        These tables are available through this book: Kinnard, Margaret F. and O'Brien, Timothy G. 'The Ecology and Conservation of Asian Hornbills, Farmers of the Forest'. 2007: The University of Chicago Press, Chicago
      </para>
    </additionalInfo>
    <intellectualRights>
      <para>Obtain permission from data set owner(s)</para>
    </intellectualRights>
    <distribution scope="document">
      <offline>
        <mediumName>hardcopy</mediumName>
      </offline>
    </distribution>
    <coverage scope="document">
      <temporalCoverage scope="document">
        <singleDateTime>
          <calendarDate>2007</calendarDate>
        </singleDateTime>
      </temporalCoverage>
      <taxonomicCoverage scope="document">
        <taxonomicClassification>
          <taxonRankName>Genus</taxonRankName>
          <taxonRankValue>Anorrhinus</taxonRankValue>
        </taxonomicClassification>
        <taxonomicClassification>
          <taxonRankName>Genus</taxonRankName>
          <taxonRankValue>Ocyceros</taxonRankValue>
        </taxonomicClassification>
        <taxonomicClassification>
          <taxonRankName>Genus</taxonRankName>
          <taxonRankValue>Anthracoceros</taxonRankValue>
        </taxonomicClassification>
        <taxonomicClassification>
          <taxonRankName>Genus</taxonRankName>
          <taxonRankValue>Buceros</taxonRankValue>
        </taxonomicClassification>
        <taxonomicClassification>
          <taxonRankName>Genus</taxonRankName>
          <taxonRankValue>Rhinoplax</taxonRankValue>
        </taxonomicClassification>
        <taxonomicClassification>
          <taxonRankName>Genus</taxonRankName>
          <taxonRankValue>Penelopides</taxonRankValue>
        </taxonomicClassification>
        <taxonomicClassification>
          <taxonRankName>Genus</taxonRankName>
          <taxonRankValue>Berenicornis</taxonRankValue>
        </taxonomicClassification>
        <taxonomicClassification>
          <taxonRankName>Genus</taxonRankName>
          <taxonRankValue>Aceros</taxonRankValue>
        </taxonomicClassification>
        <taxonomicClassification>
          <taxonRankName>Genus</taxonRankName>
          <taxonRankValue>Rhyticeros</taxonRankValue>
        </taxonomicClassification>
      </taxonomicCoverage>
      <geographicCoverage scope="document">
        <geographicDescription>Asian Forests</geographicDescription>
        <boundingCoordinates>
          <westBoundingCoordinate>74.125</westBoundingCoordinate>
          <eastBoundingCoordinate>156.75</eastBoundingCoordinate>
          <northBoundingCoordinate>17.625</northBoundingCoordinate>
          <southBoundingCoordinate>-11.25</southBoundingCoordinate>
        </boundingCoordinates>
      </geographicCoverage>
    </coverage>
    <contact id="1207779746470" scope="document">
      <individualName>
        <givenName>Margaret F.</givenName>
        <surName>Kinnaird</surName>
      </individualName>
      <electronicMailAddress>mkinnaird@wcs.org</electronicMailAddress>
    </contact>
    <contact scope="document">
      <references>1207779666443</references>
    </contact>
    <access authSystem="knb" order="denyFirst" scope="document">
      <allow>
        <principal>uid=nceasadmin,o=NCEAS,dc=ecoinformatics,dc=org</principal>
        <permission>all</permission>
      </allow>
      <allow>
        <principal>uid=nceasadmin,o=NCEAS,dc=ecoinformatics,dc=org</principal>
        <permission>all</permission>
      </allow>
      <allow>
        <principal>public</principal>
        <permission>read</permission>
      </allow>
    </access>
  </dataset>
</eml:eml>
```

We produce triples in the following three graphs:

People:

```{ttl}
<https://dataone.org/person/urn:uri:cafd2962-4985-4175-b33b-f95481587abe>
        <http://schema.geolink.org/dev/view/isCreatorOf>
                <https://cn.dataone.org/cn/v1/resolve/doi:10.5063/AA/nceas.920.2> ;
        <http://schema.geolink.org/dev/view/nameFamily>
                "Kinnaird" ;
        <http://schema.geolink.org/dev/view/nameFull>
                "Margaret F. Kinnaird" ;
        <http://schema.geolink.org/dev/view/nameGiven>
                "Margaret" ;
        <http://xmlns.com/foaf/0.1/mbox>
                <mailto:mkinnaird@wcs.org> .

<https://dataone.org/person/urn:uri:73cb4630-1aa2-42d7-8752-21bc6f764dda>
        <http://schema.geolink.org/dev/view/isCreatorOf>
                <https://cn.dataone.org/cn/v1/resolve/doi:10.5063/AA/nceas.920.2> ;
        <http://schema.geolink.org/dev/view/nameFamily>
                "O'Brien" ;
        <http://schema.geolink.org/dev/view/nameFull>
                "Timothy G. O'Brien" ;
        <http://schema.geolink.org/dev/view/nameGiven>
                "Timothy" ;
        <http://xmlns.com/foaf/0.1/mbox>
                <mailto:tobrian@wcs.org> .

```

Organizations:

```{ttl}
<https://dataone.org/organization/urn:uri:fcc5efe4-6d83-4939-a798-c024afba1c8d>
        <http://www.w3.org/2000/01/rdf-schema#label>
                "National Center for Ecological Analysis and Synthesis" ;
        <http://schema.geolink.org/dev/view/isCreatorOf>
                <https://cn.dataone.org/cn/v1/resolve/doi:10.5063/AA/nceas.920.2> .
```

Datasets:

```{ttl}
<https://cn.dataone.org/cn/v1/resolve/doi%3A10.5063%2FAA%2Fnceas.920.2>
        a       <http://schema.geolink.org/dev/view/Dataset> ;
        <http://www.w3.org/2000/01/rdf-schema#label>
                "The Ecology and Conservation of Asian Hornbills Book" ;
        <http://schema.geolink.org/dev/view/description>
                "This book contains a number of data tables regarding Asian Hornbills and their relationship to the Asian ecosystem. The tables included in this publication are titled: 1.1 Scientific and Common names for 31 species (including subspecies) within their distribution and habitats; 2.1 Forty years of shifting hornbill taxonomy; 2.2 Mean wing and body size for samples of male and female Asian Hornbills; 2.3 Results of principal components analysis of degree of sexual dimorphism and generic-level differences; 2.5 Morphological differences and occurrence of territoriality among Asian hornbills; 3.1 Rainfall seasonality across the hornbill realm for 61 sites in 12 countries; 3.2 Summary of selected phenological studies in Asia; 4.1   Comparison of fruit and animal matter in the diets of 17 species of Asian hornbills during breeding and nonbreeding seasons; 4.2 Number of genera and species in 46 families of fruiting plants identified in the diets of 17 species of well-studied Asian hornbills; 4.3 Dietary diversity reported in 26 studies of 16 Asian hornbill species; 4.4 Diet overlap for 43 hornbill species pairs from 7 locations;  4.5 Description of vegetation plots used for estimating fruit availability in Tankoko, Sulawesi, and BBSNP Sumatra; 4.6 Estimates of monthly fruit availability in Tangkoko, Sulawesi, and BBSNP, Sumatra; 4.7 Estimates of hornbill biomass for Tangkoko and BBSNP study sites; 5.1 Nesting season in reltion to the onset of rain for 22 species of Asian hornbills by country and position relative to equator; 5.2 Measures of fruit availability during courtship, nesting, and fledging periods; 5.4 Nest characteristics for 14 hornbill species studied at 8 forest sites; 5.4 Maximum clutch size and egg volume for 26 hornbill species; 5.5 Breeding parameters for 22 hornbill species; 6.1 Nesting success in four orders of birds; 6.2 Cooperatively breeding hornbills  within the family Bucerotidae; 7.1 Movement patterns of six adult male Red-knobbed Hornbills and two Sulawesi Tarictic Hornbill families; 7.2 Description of four hornbill diet tree species used for modeling ecologically functional populations; 7.3 Size-class distributions and probabilities of survivial (l%26#226;%26#130;%26#147;) and mortality (m%26#226;%26#130;%26#147;) for four hornbill diet species used to model ecologically functional hornbill populations; 7.4 Dispersal and germination of four species of hornbill diet trees; 8.1 Human population statistics and forest area in the hornbill realm; 8.2 Conservation status of 31 species of Asian hornbills based on the IUCN Red List of Threatened Species; 8.3 Measures of current range size and habitat configuration for Asian hornbills; 8.4 Characteristics of hornbill neighborhoods; 8.5 Suggested changes in the IUCN Red List of Threatened Species categories of 31 species of Asian hornbills; 9.1 Range, IUCN protected areas, and proportion of suitable habitat in those area for 31 Asian hornbill species." ;
        <http://schema.geolink.org/dev/view/hasAuthoritativeDigitalRepository>
                <https://cn.dataone.org/cn/v1/node/urn:node:KNB> ;
        <http://schema.geolink.org/dev/view/hasEndDate>
                "2007-01-01T00:00:00Z" ;
        <http://schema.geolink.org/dev/view/hasGeometryAsWktLiteral>
                "POLYGON ((74.125 17.625, 156.75 17.625, 156.75 -11.25, 74.125, -11.25))" ;
        <http://schema.geolink.org/dev/view/hasIdentifier>
                [ a       <http://schema.geolink.org/dev/view/Identifier> ;
                  <http://www.w3.org/2000/01/rdf-schema#label>
                          "doi:10.5063/AA/nceas.920.2" ;
                  <http://schema.geolink.org/dev/view/hasIdentifierScheme>
                          <http://purl.org/spar/datacite/doi> ;
                  <http://schema.geolink.org/dev/view/hasIdentifierValue>
                          "doi:10.5063/AA/nceas.920.2"
                ] ;
        <http://schema.geolink.org/dev/view/hasLandingPage>
                <https://search.dataone.org/#view/doi%3A10.5063%2FAA%2Fnceas.920.2> ;
        <http://schema.geolink.org/dev/view/hasOriginDigitalRepository>
                <https://cn.dataone.org/cn/v1/node/urn:node:KNB> ;
        <http://schema.geolink.org/dev/view/hasReplicaDigitalRepository>
                <https://cn.dataone.org/cn/v1/node/urn:node:KNB> ;
        <http://schema.geolink.org/dev/view/title>
                "The Ecology and Conservation of Asian Hornbills Book" ;
        <http://www.w3.org/ns/prov#wasRevisionOf>
                <https://cn.dataone.org/cn/v1/resolve/doi:10.5063/AA/nceas.920.1> .
```
