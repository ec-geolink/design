# Canonical Identifiers Forms

## Overview

Identifiers (e.g., DOI, ORCID, etc.) will be used in GeoLink LOD graphs and we would like to have a set of guidelines for how each type of identifier should show up in our graphs. See #51 for discussion on this topic.

In general, identifiers have attributes such as a schema, some concept resembling a value (sometimes normalized and then used for comparison of identifiers), a display form (for print), and one of more HTTP-resolvable URI forms. However, it is often the case that the a specification detailing these forms does not exist or does not provide guidance on all of the aforementioned attributes. Commonly, all that is made available is a specification of a schema and a value and recommendations about how to display an identifier in print (or in RDF) are left undiscussed.

While it may be difficult to decide on the best way to serialize identifiers in GeoLink, deciding as a group on a single way to do things will ensure we're doing something reasonable and that we're all doing the same reasonable thing in our graphs. In this document I present a list of identifiers, information about their specification and attributes, and provide my recommendations for how we should serialize them in our graphs.

For each identifier, I:

- Tried to find a best source of information for the identifier and included a link if I found one
- Tried to find an example usage of the identifier in the wild
- Tried to make the distinction between use cases and make sure we had the best form for use in an LOD graph
- Tried to find an endpoint that responds with RDF/XML or some other serialization of triples for each identifier

I then wrote recommendations for what values to fill in as properties of `glbase:Identifier` resources we put in our graphs.

The current set of properties are:

- `glbase:hasIdentifierScheme`: Captures the scheme (e.g., DOI) for an identifier. Always use [DataCite named individuals](http://www.essepuntato.it/lode/http://purl.org/spar/datacite#namedindividuals). Use `datacite:local-resource-identifier` for internal identifiers (e.g., some DataONE PIDs)
- `glbase:hasIdentifierValue`: Defined in the ontology as: "Points to the actual string value of identifier., e.g.: &quot;doi:10.5063/AA/ArchivalTag.4.1&quot;". This is vague.

I propose we break up `glbase:hasIdentifierValue` into two properties, `glbase:hasIdentifierValue` and `glbase:hasIdentifierResolveURI`. I welcome feedback on the names of the properties (esp the latter) and also the number of properties we need to properly serialize identifiers in our graphs.

- `glbase:hasIdentifierValue`: Captures the canonical form of the identifier. Subject to three principles:
  1. Avoid using HTTP resolve URIs: e.g., prefer `'doi:10.1006/jmbi.1998.2354'` to '[http://doi.org/10.1006/jmbi.1998.2354](http://doi.org/10.1006/jmbi.1998.2354)'
  2. Avoid forms that need other information to be recognized as an identifier of its scheme: e.g., prefer `doi:10.1006/jmbi.1998.2354` to `10.1006/jmbi.1998.2354`
  3. If an identifier has an established URI scheme, use it, and if it doesn't, don't make something up.

- `glbase:hasIdentifierResolveURI`: If present, include the preferred HTTP URI at which the identifier can be resolved in some way. Always starts with 'http(s)://' and may return anything relevant to the identifier.

For dataset (`:x`) with a DOI identifier that has the DOI name '10.1006/jmbi.1998.2354', the corresponding (elided) Turtle serialization would look like this:

```{ttl}
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix glbase: <http://schema.geolink.org/dev/view.owl > .
@prefix datacite: <http://purl.spar.org/datacite/> .

:x a glbase:Dataset ;
  #...elided...
  glbase:hasIdentifier [
    glbase:hasIdentifierScheme datacite:doi ;
    glbase:hasIdentifierValue "doi:10.1006/jmbi.1998.2354" ;
    glbase:hasIdentifierResolveURI <http://doi.org/10.1006/jmbi.1998.2354> .
  ] ;
  #...elided...
```

### Contents
Here's the set of identifiers the GeoLink project has expressed interest in putting into our graphs. The list started as a 1:1 copy of the identifiers listed at [http://purl.org/spar/datacite](http://purl.org/spar/datacite) but has expanded to a few identifiers requested by members of the GeoLink team.
- [ARK](#ark)
- [arXiv](#arxiv)
- [DAI](#dai)
- [DOI](#doi)
- [EAN13](#ean13)
- [EISSN](#eissn)
- [FundRef](#fundref)
- [GVP](#gvp)
- [Handle](#handle)
- [IGSN](#igsn)
- [IMA](#ima)
- [InfoURI](infouri)
- [InterRidge](#interridge)
- [ISNI](#isni)
- [ISSN](#issn)
- [ISSN-L](#issn-l)
- [ISTC](#istc)
- [JST](#jst)
- [LSID](#lsid)
- [National Insurance Number](#national-insurance-number)
- [OpenID](#openid)
- [ORCID](#orcid)
- [PII](#pii)
- [PMCID](#pmcid)
- [PMID](#pmid)
- [PURL](#purl)
- [ResearcherID](#researcherid)
- [SCAR](#scar)
- [SICI](#sici)
- [SSN](#ssn)
- [UPC](#upc)
- [URI](#uri)
- [URL](#url)
- [URN](#urn)
- [UUID](#uuid)
- [VIAF](#viaf)

### A Note on Web-Resolvable Identifiers

It might be really nice to ensure we take a similar approach for all identifiers that have resolution services (e.g. DOI, Handle). This gets tricky because a number of services use identifiers of this form but they recommend slightly different use patterns.

For example, DOI suggests using [http://doi.org/{DOI}](http://doi.org/{DOI}) while FundRef uses [http://dx.doi.org/{DOI}](http://dx.doi.org/{DOI}) as their identifiers. It may be confusing to store DOIs in different forms but in a way, a DOI that is used as a FundRef DOI Is more of a 'FundRef DOI' rather than an 'DOI DOI'.

## ARK
Source: [https://confluence.ucop.edu/display/Curation/ARK](https://confluence.ucop.edu/display/Curation/ARK) (See: ARK Anatomy)

Notes:

- "The immutable, globally unique identifier follows the "ark:" label."
  - ark:/12025/654xz321/s3/f8.05v.tiff

- "When embedded in a URL, it is preceded by the protocol  ("http://") and name of a service that provides support for that ARK." e.g.
  - [http://example.org/ark:/12025/654xz321/s3/f8.05v.tiff](http://example.org/ark:/12025/654xz321/s3/f8.05v.tiff)

- "The NMA part, which makes the ARK actionable (clickable in a web browser), is in brackets to indicate that it is optional and replaceable"

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"ark:/12025/654xz321/s3/f8.05v.tiff"`
`hasIdentifierResolveURI` | `<http://example.org/ark:/12025/654xz321/s3/f8.05v.tiff>`


## arXiv

Sources:

- [http://arxiv.org/help/arxiv_identifier_for_services](http://arxiv.org/help/arxiv_identifier_for_services)
- [http://arxiv.org/help/faq/references](http://arxiv.org/help/faq/references)
- [http://arxiv.org/help/arxiv_identifier](http://arxiv.org/help/arxiv_identifier)

Notes:

- arXiv makes the distinction between internal and external identifier forms where an internal identifier could be 'hep-th/9901001' and the external form for the same identifier is 'arXiv:hep-th/9901001' (Source: http://arxiv.org/help/arxiv_identifier_for_services)
- arXiv changes their format over time and article identifiers are not updated.
- "The form of arXiv identifiers for new articles changed on 1 April 2007, and the number of digits in the sequence number changed again on 1 January 2015. All existing articles retain their identifiers."
- arXiv uses arXiv:hep-th/9901001v2 to link to [http://arxiv.org/abs/hep-th/9901001v2](http://arxiv.org/abs/hep-th/9901001v2)

Example: arXiv:1207.2147 General form: arXiv:YYMM.number

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"arXiv:1501.00001"`
`hasIdentifierResolveURI` | `<http://arxiv.org/abs/1501.00001>`


## DAI

Source: [https://wiki.surfnet.nl/display/standards/DAI](https://wiki.surfnet.nl/display/standards/DAI)

Notes:

- "The DAI (or PPN) contains 9 to 10 characters. The first 8 to 9 characters are numbers. The last (9th or 10th) character is a control character. The control character is a modulus 11 check digit, like in the ISBN."
- "The DAI is the number after the string info:eu-repo/dai/nl/ . A DAI is a number like 123456785. The last character is a MOD11 check-digit.
- The string: info:eu-repo/dai/nl/ is just an authority namespace, telling the user or machine that the number is a DAI originating from the Netherlands."
- So the DAI is 9-10 chars. If it's URI-ified, it'll have something like 'info:eu-repo/dai/nl/' prepended to it.
- I found an example of one on narcis.nl: info:eu-repo/dai/nl/275853993

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"info:eu-repo/dai/nl/275853993"`
`hasIdentifierResolveURI` |


## DOI

Notes:

> To resolve a DOI via a standard web hyperlink, the DOI name itself should be appended to the address for the proxy server.     EXAMPLE     The DOI name "10.1006/jmbi.1998.2354" would be made an actionable link as "[http://doi.org/10.1006/jmbi.1998.2354](http://doi.org/10.1006/jmbi.1998.2354)".

> Source: [http://www.doi.org/doi_handbook/2_Numbering.html](http://www.doi.org/doi_handbook/2_Numbering.html)

> So while it may be awkward, we recommend some convention of showing both the plain DOI name and a way to resolve it online (a shorthand way of saying "the DOI name for this article is 10.1002/prot.999 and current information may be found on the web through [http://doi.org/10.1002/prot.999](http://doi.org/10.1002/prot.999)" or "...available via [http://doi.org/](http://doi.org/)...".

- DOI doesn't promise the resolve URL will work forever so they recommend the above.
- DOI.org prefers resolving at doi.org/ instad of dx.doi.org, even though the maintain dx.doi.org. (Source: [http://www.doi.org/factsheets/DOIProxy.html](http://www.doi.org/factsheets/DOIProxy.html))
- CrossRef is much more didactic about what to do at [http://www.crossref.org/02publishers/doi_display_guidelines.html](http://www.crossref.org/02publishers/doi_display_guidelines.html) where they recommend always using the dx.doi.org/ URL when (among other things) "Anywhere users are directed to a permanent, stable, or persistent link to the content".
- DOIs are meant to be resolvable on the web. (Source: [http://www.doi.org/doi_handbook/1_Introduction.html](http://www.doi.org/doi_handbook/1_Introduction.html))

Resolve URL: [http://dx.doi.org/10.1093%2Fnar%2Fgks1195](http://dx.doi.org/10.1093%2Fnar%2Fgks1195)

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"doi:10.1006/jmbi.1998.2354"`
`hasIdentifierResolveURI` | `<http://dx.doi.org/10.1006/jmbi.1998.2354>`


## EAN13

Source: [http://www.gs1.org/barcodes/ean-upc](http://www.gs1.org/barcodes/ean-upc)

General form: 13-digit (12 data, 1 check) number

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"9501101530003"`
`hasIdentifierResolveURI` |


## EISSN

Sources:

- [http://www.issn.org/understanding-the-issn/what-is-an-issn/](http://www.issn.org/understanding-the-issn/what-is-an-issn/)
- [http://www.issn.org/understanding-the-issn/assignment-rules/the-issn-for-electronic-media/](http://www.issn.org/understanding-the-issn/assignment-rules/the-issn-for-electronic-media/)

Notes:

> What form does an ISSN take? The ISSN takes the form of the acronym ISSN followed by two groups of four digits, separated by a hyphen. The eighth digit is a check digit calculated according to a modulus 11 algorithm on the basis of the 7 preceding digits; this eighth control digit may be an "X" if the result of the computing is equal to "10", in order to avoid any ambiguity.

> e. g.:

> ISSN 0317-8471

> ISSN 1050-124X

- I just found this on CrossRef: [https://api.crossref.org/v1/works/http://dx.doi.org/10.3390/e17041701](https://api.crossref.org/v1/works/http://dx.doi.org/10.3390/e17041701). The ISSN is given as just '1099-4300'. Maybe that's the best way.

- Use `0317-8471` because the ISSN part is redundant and I've seen a use in the wild (see above) that omits the 'ISSN' before the numbers.

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"1099-4300"`
`hasIdentifierResolveURI` |


## FundRef

Source: [http://www.crossref.org/fundref/](http://www.crossref.org/fundref/)

Notes:

- FundRef offers up its own (internal) identiifers, e.g. 501100004802, but these do not appear to be FundRef identifiers but just internal identifiers instead. e.g.
- [http://search.crossref.org/fundref?q=501100004802](http://search.crossref.org/fundref?q=501100004802)
- FundRef is just a mapping service between the funder and their canonical name. For example, FundRef maintains the mapping '[http://dx.doi.org/10.13039/100000001](http://dx.doi.org/10.13039/100000001)' to `National Science Foundation`. All the mappings in their system uses the dx.doi base URL.
- When you resolve a FundRef DOI, they report back with an `id` in the form of '[http://dx.doi.org/10.13039/100000001](http://dx.doi.org/10.13039/100000001)'.


Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"doi:10.13039/100000001"`
`hasIdentifierResolveURI` | `<http://doi.org/10.13039/100000001>`

## GVP

Sources:

- No good source describing identifier structure/representation.
- [http://volcano.si.edu/gvp_vnums.cfm](http://volcano.si.edu/gvp_vnums.cfm)
- [http://volcano.si.edu/list_volcano_holocene.cfm](http://volcano.si.edu/list_volcano_holocene.cfm)

About:

Smithsonian's Global Volcanism Program (GVP) announces new and permanent unique identifiers (Volcano Numbers, or VNums) for volcanoes documented in the Volcanoes of the World (VOTW) database maintained by GVP and accessible at www.volcano.si.edu.

Examples:

- GVP:210010
- [http://volcano.si.edu/volcano.cfm?vn=210010](http://volcano.si.edu/volcano.cfm?vn=210010)

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"GVP:210010"`
`hasIdentifierResolveURI` | `<http://volcano.si.edu/volcano.cfm?vn=210010>`


## Handle

Sources:

- https://www.handle.net/rfc/rfc3650.html
- http://www.ietf.org/rfc/rfc3651.txt

Notes:

- Other identifiers, such as DOIs, are Handles
- Example: '10.1045/may99-payette'
- "CNRI runs a proxy server system at http://hdl.handle.net/" (Source: https://www.handle.net/proxy.html) that can resolve URLs like http://hdl.handle.net/4263537/5555
- "Like DNS or X.500 directory service, the Handle System defines its namespace outside of any URI/URN namespace."

It appears handles have no URN-style prefix we can use.

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"10.1045/may99-payette"`
`hasIdentifierResolveURI` | `<http://hdl.handle.net/10.1045/may99-payette>`


## IGSN

Sources:

- [http://www.geosamples.org/igsnabout](http://www.geosamples.org/igsnabout)
- [http://www.geosamples.org/aboutigsn](http://www.geosamples.org/aboutigsn)

About:

IGSN stands for _International Geo Sample Number_. The IGSN is 9-digit alphanumeric code that uniquely identifies samples from our natural environment and related sampling features. You can get an IGSN for your sample by registering it in the System for Earth Sample Registration SESAR.

Notes:

- The IGSN is 9-digit alphanumeric code that uniquely identifies samples from our natural environment and related sampling features.
- IGSN's can have URIs, though not consistently: [http://www.geosamples.org/profile?igsn=IECUR001E](http://www.geosamples.org/profile?igsn=IECUR001E)
- The IGSN follows the syntax of the URN (Uniform Resource Name) which is composed of a 'Namespace Identifier' (NID), a unique, short string, and the 'Namespace Specific String' (NSS).
- "...the first five digits of the IGSN represent a name space (a unique user code) that uniquely identifies the person or institution that registers the sample."
- "The last 4 digits of the IGSN are a random string of alphanumeric characters (0-9, A-Z)."
- "IGSN namespaces that were obtained before July 2014 may have three digit namespaces followed by a random string of 6 alphanumeric characters (e.g. examples #1 and # 2 above). For more information see [http://www.geosamples.org/news/namespacechanges](http://www.geosamples.org/news/namespacechanges)."

Examples:

- IGSN:HRV003M16
- IGSN: IECUR001E (has extra space)

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"IGSN:HRV003M16"`
`hasIdentifierResolveURI` |


## IMA

Sources:

- [http://www.ima-mineralogy.org/Minlist.htm](http://www.ima-mineralogy.org/Minlist.htm)

About:

International Mineralogical Association (IMA) publish the list contains names and data for minerals which have been approved, discredited, redefined and renamed and is the new revised master list of all IMA-approved and grandfathered (i.e. inherited from before 1960) minerals.

Examples:

- IMA:2014-028
- IMA1975-013 (on [http://rruff.info/ima/](http://rruff.info/ima/))
- 'No. 2014-103' in print.

Notes:

- "The continuing integrity of the (web-based) IMA mineral list will be maintained by the IMA outreach committee, and additional features are being developed by the RRUFF™ Project."
- It does not publish the URIs that speak RDF


Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"IMA:2014-028"`
`hasIdentifierResolveURI` |


## InfoURI

Source: [http://info-uri.info/registry/docs/misc/faq.html](http://info-uri.info/registry/docs/misc/faq.html)

Scheme: `info-scheme ":" info-identifier [ "#" fragment ]`

Examples:

- info:ddc/22/eng//004.678
- info:lccn/2002022641

They seem to recommend included the `info` (info-scheme) when encoding in RDF, for example.

```{rdf}
<rdf:Description about="info:pii/S0888-7543(02)96852-7">
```

Notes on Normalization:

> The following generic normalization steps should be applied:
  1. Normalize the case of the "scheme" component to be lowercase.
  2. Normalize the case of the "namespace" component to be lowercase.
  3. Unescape all unreserved %-escaped characters in the "namespace" and "identifier" components.
  4. Normalize the case of any %-escaped characters in the "namespace" and "identifier" components to be uppercase.
  5. The subsequent namespace-specific normalization steps may be applied:
  6. Normalize the case of the "identifier" component as per any rules that may be recorded in the Registry.
  7. Normalize any punctuation characters in the "identifier" component as per any rules that may be recorded in the Registry.


Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"info:pii/S0888-7543(02)96852-7"`
`hasIdentifierResolveURI` |


## InterRidge

Sources:

- [http://vents-data.interridge.org/sites/vents-data.interridge.org/files/InterRidge_Vents_Database_Version3.1_documentation.pdf](http://vents-data.interridge.org/sites/vents-data.interridge.org/files/InterRidge_Vents_Database_Version3.1_documentation.pdf)
- [http://vents-data.interridge.org/about_the_database](http://vents-data.interridge.org/about_the_database)

About:

The InterRidge Global Database of Active Submarine Hydrothermal Vent Fields, hereafter referred to as the "InterRidge Vents Database," is to provide a comprehensive list of active and inferred active (unconfirmed) submarine hydrothermal vent fields for use in academic research and education.

Examples:

- InterRidge:13-n-ridge-site
- [http://vents-data.interridge.org/ventfield/13-n-ridge-site](http://vents-data.interridge.org/ventfield/13-n-ridge-site)

Notes:

- It speaks RDF from version 3, and provide SPARQL endpoint [http://vents-data.interridge.org/sparql](http://vents-data.interridge.org/sparql)
- "In the vents database, the URIs are comprised of the site
- namespace, which should be persistent ... and the node ID (nid) for each vent field (i.e., the
- node ID for each vent field is effectively the unique identifier for that vent field) or unique name of
- the vent field using path alias, e.g., Mariner is [http://irvents-new3.whoi.edu/node/1001](http://irvents-new3.whoi.edu/node/1001) and
- [http://irvents-new3.whoi.edu/ventfield/mariner](http://irvents-new3.whoi.edu/ventfield/mariner)."

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"InterRidge:13-n-ridge-site"`
`hasIdentifierResolveURI` |


## ISBN

Source: [https://www.isbn-international.org/sites/default/files/ISBN%20Manual%202012%20-corr.pdf](https://www.isbn-international.org/sites/default/files/ISBN%20Manual%202012%20-corr.pdf)

Notes:

- "When printed, the ISBN is always preceded by the letters "ISBN"."
  - e.g. ISBN 978-0-571-08989-5

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"978-0-571-08989-5"`
`hasIdentifierResolveURI` |


## ISNI

Sources:

- http://www.isni.org/how-isni-works

Notes:

> Linked data is part of the ISNI-IA’s strategy to make ISNIs freely available and widely diffused.  Each assigned ISNI is accessible by a persistent URI in the form http://isni.org/isni/[isni]  for example: http://isni.org/isni/0000000121032683.   ISNI core metadata is available in html, xml and RD/XML.

- ISNI has publicly committed to implementing URIs that speak RDF (Source: [https://lists.w3.org/Archives/Public/public-lod/2013Dec/0047.html](https://lists.w3.org/Archives/Public/public-lod/2013Dec/0047.html)).

Examples:

- ISNI 0000 0003 9591 6013
- ISN:0000000395916013
- [http://isni.org/isni/0000000124514311](http://isni.org/isni/0000000124514311)

Notes:

- For [http://isni.org/isni/](http://isni.org/isni/) URLs, ISNI doesn't make it very clear what that service is or how committed they are to keeping it up.


Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"ISN:0000000395916013"`
`hasIdentifierResolveURI` | `<http://isni.org/isni/0000000395916013>` (no www)


## ISSN

Source: [http://www.issn.org/understanding-the-issn/assignment-rules/issn-manual/](http://www.issn.org/understanding-the-issn/assignment-rules/issn-manual/)

Notes:

- 'An ISSN consists of eight digits. These are the Arabic numerals 0 to 9, except that an upper case X can sometimes occur in the final position as a check digit.'
- When using in a DOI, ISSN recommends making the DOI look like 'http://dx.doi.org/10.5930/issn.1994-4683', note the dash (Source: http://www.issn.org/understanding-the-issn/issn-uses/use-of-issn-in-doi/)
- BibFrame uses the dashed from in their RDF: http://bibframe.org/vocab/issn.html
- [This page](http://inkdroid.org/2011/04/25/dois-as-linked-data/) shows some examples of the hyphenated forms.

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"1562-6865"`
`hasIdentifierResolveURI` |


## ISSN-L

See above (ISSN)

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"1748-7188"`
`hasIdentifierResolveURI` |


## ISTC

Source: [http://www.istc-international.org/html/about_structure_syntax.aspx](http://www.istc-international.org/html/about_structure_syntax.aspx)

Notes:

- The [official website](http://www.istc-international.org/) is down at the moment (2015-11-25 11:11AM AKST)

Examples:

- ISTC A02-2009-000004BE-A
- A02-2009-000004BE-A
- A02 2009 000004BE A
- A022009000004BEA

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"A022009000004BEA"`
`hasIdentifierResolveURI` |


## JST

Not sure on this one. Having a hard time finding anything.

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | None (To be done)
`hasIdentifierResolveURI` |


## LSID

Sources:

- https://en.wikipedia.org/wiki/LSID

Notes:

- 'Life Sciences Identifiers are case-insensitive for the first three portions of the identifier ("URN", "LSID", authority identification). The remainder of the identifier (namespace identification, object identification, revision identification) is case sensitive.'
- They are of the form `urn:lsid:<Authority>:<Namespace>:<ObjectID>[:<Version>]`
- LSIDs may be resolved by HTTP URIs, e.g. `<http://zoobank.org/urn:lsid:zoobank.org:pub:CDC8D258-8F57-41DC-B560-247E17D3DC8C>`

Recommendation:

- Downcase urn and lsid, but leave the rest in-tact.

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"urn:lsid:zoobank.org:pub:CDC8D258-8F57-41DC-B560-247E17D3DC8C"`
`hasIdentifierResolveURI` | `<http://zoobank.org/urn:lsid:zoobank.org:pub:CDC8D258-8F57-41DC-B560-247E17D3DC8C>`


## National Insurance Number

Source: [http://www.hmrc.gov.uk/manuals/nimmanual/NIM39110.htm](http://www.hmrc.gov.uk/manuals/nimmanual/NIM39110.htm)

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"QQ123456A"`
`hasIdentifierResolveURI` |


## NIHMSID

Sources:

- http://www.ncbi.nlm.nih.gov/pmc/about/public-access-info/#p3

Notes:

- "The NIHMSID is a preliminary article identifier that applies only to manuscripts deposited through the NIHMS system. "
- "The NIHMSID is only valid for compliance reporting for 90 days after the publication date of an article. Once the Web version of the NIHMS submission is approved for inclusion in PMC and the corresponding citation is in PubMed, the article will also be assigned a PMCID."
- When cited, NIHMSIDs are cited as 'NIHMSID: NIHMS44135'
- There is a converter service to convert between PMID, PMCIDs, NIHMSIDs, etc. In that converter, you only have to enter '44135' to get it to find the NIHMSID with that number. I would say this is evidence that '44135' is the identifier itself.

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"44135"` (no 'NIHMS' prefix)
`hasIdentifierResolveURI` |


# OpenID

Notes:

- Under OpenID Auth 1.1 ([http://openid.net/specs/openid-authentication-1_1.html](http://openid.net/specs/openid-authentication-1_1.html)), OpenID Identifiers are just URLs and follow the same rules.

Recommendation:

- Format as URLs

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"http(s)://example.org"`
`hasIdentifierResolveURI` |


# ORCID

Notes:

- ORCIDs are usually serialized as either:
  - [http://orcid.org/0000-0001-9923-4648](http://orcid.org/0000-0001-9923-4648) or
  - 0000-0001-9923-4648

- ORCID responds to RDF/XML if you send an accept header to them (redirects to something like [https://pub.orcid.org/experimental_rdf_v1/0000-0001-9923-4648](https://pub.orcid.org/experimental_rdf_v1/0000-0001-9923-4648)).

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"0000-0002-2389-8429"`
`hasIdentifierResolveURI` | `<http://orcid.org/0000-0002-2389-8429>`


## PII

Sources:

- http://web.archive.org/web/20031013073003/http://www.elsevier.nl/inca/homepage/about/pii/

Notes:

- This appears to be a "Publisher Item Identifier" (https://en.wikipedia.org/wiki/Publisher_Item_Identifier)
- PII's contain ISBNs or ISSN in their strings

Examples:

- Serial w/ ISSN: Sxxxx-xxxx(yy)iiiii-d
- Book w/ ISSN: B x-xxx-xxxxx-x/iiiii-d
- In print:
	- "PII: Sxxxx-xxxx(yy)iiiii-d"
	- "B x-xxx-xxxxx-x/iiiii-d"

Recommendation:

- Just store the 17 characters (no hyphens, slashes).

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"Sxxxx-xxxx(yy)iiiii-d"`
`hasIdentifierResolveURI` |


## PMCID

These need to be distinguished from PMIDs. That is done by prepending PMC to the ID, e.g. PMC3531190.

Resolve URL: [http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3531190/](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3531190/)

Notes:

- As with NIHMSIDs, PMCIDs often shown prepended with the text PMC to distinguish them from similar identifers (in this case, PMIDs).


Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"3531190"`
`hasIdentifierResolveURI` | `<http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3531190/>`


## PMID
These appear to just be a string of numbers, e.g. 23193287.

Resolve URL: http://www.ncbi.nlm.nih.gov/pubmed/23193287

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"23193287"`
`hasIdentifierResolveURI` | `<http://www.ncbi.nlm.nih.gov/pubmed/23193287>`


## PURL

Source: [https://sites.google.com/site/persistenturls/](https://sites.google.com/site/persistenturls/)

Notes:

- All PURLs are URLs.

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"http(s)://example.org/"`
`hasIdentifierResolveURI` |


## ResearcherID

Sources:

- https://en.wikipedia.org/wiki/ResearcherID
- http://thomsonreuters.com/en/products-services/scholarly-scientific-research/authoring-and-collaboration-tools/researcherid.html

Notes:

- ResearcherID are commonly serialized and shared as X-XXXX-XXXX
- It's not clear if there are any other forms

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"X-XXXX-XXXX"`
`hasIdentifierResolveURI` |


## SCAR

Sources:

- No good source describing identifier structure/representation.
- [https://www1.data.antarctica.gov.au/aadc/gaz/scar/information.cfm](https://www1.data.antarctica.gov.au/aadc/gaz/scar/information.cfm)

About:

The Scientific Committee on Antarctic Research (SCAR),  through its recommendations, expresses the hope that the present effort will contribute to the adoption in Antarctica of the general principle of 'one name per feature' by all Antarctic place naming authorities.

Notes:

- It does not publish URIs that speak RDF

Examples:

- SCAR:883



Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"SCAR:883"`
`hasIdentifierResolveURI` |


## SICI

I think this is the Serial Item and Contribution Identifier (https://en.wikipedia.org/wiki/Serial_Item_and_Contribution_Identifier)

Sources:

- http://www.niso.org/apps/group_public/download.php/6514/Serial%20Item%20and%20Contribution%20Identifier%20%28SICI%29.pdf

Notes:

- There are threes forms, CSI-1 and CSI-2, and CSI-3:
	- CSI-1: 1234-5679(19950221)1:2:3<>1.0.TX;2-A
	- CSI-2: 1234-5679(19950221)1:2:3<123:ABCDEF>2.0.TX;2-A
	- CSI-3: 1234-5679(1996)<::INS-023456>3.0.CO;2-#

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"0015-6914(19960101)157:1<62:KTSW>2.O.TX;2-F"`
`hasIdentifierResolveURI` |


## SSN

Sources:

- https://www.socialsecurity.gov/history/ssn/geocard.html

Notes:

- The SSN is made up of Area-Group-Serial sections.


Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"123-45-6789"`
`hasIdentifierResolveURI` |


## UPC

Sources:

- http://www.gs1-us.info/faq-upc-codes/


Notes:

- UPCs are either 8 or 12 digits (https://www.upcdatabase.com/itemform.asp)


Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"12345678"` or `"123456789012"`
`hasIdentifierResolveURI` |


## URI

Source: https://tools.ietf.org/html/rfc3986#section-1.1.1

Examples:

- `ftp://ftp.is.co.za/rfc/rfc1808.txt`
- `http://www.ietf.org/rfc/rfc2396.txt`
- `ldap://[2001:db8::7]/c=GB?objectClass?one`
- `mailto:John.Doe@example.com`
- `news:comp.infosystems.www.servers.unix`
- `tel:+1-816-555-1212`
- `telnet://192.0.2.16:80/`
- `urn:oasis:names:specification:docbook:dtd:xml:4.1.2`

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"ftp://ftp.is.co.za/rfc/rfc1808.txt"`
`hasIdentifierResolveURI` |


## URL

Source: https://www.ietf.org/rfc/rfc1738.txt

Notes:

- In general, URLs are written as follows: `<scheme>:<scheme-specific-part>`
- And then IP-based schemes use `//<user>:<password>@<host>:<port>/<url-path>` in their `<scheme-specific-part>`

Examples:

- `http://<host>:<port>/<path>?<searchpart>`
- `gopher://<host>:<port>/<gopher-path>`
- `nntp://<host>:<port>/<newsgroup-name>/<article-number>`
- `file://<host>/<path>`

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"http://<host>:<port>/<path>?<searchpart>"`
`hasIdentifierResolveURI` |


## URN

Sources:

- https://tools.ietf.org/html/rfc2141
- https://www.ietf.org/rfc/rfc3406.txt

Notes:

- URNs are URIs
- General form: `<URN> ::= "urn:" <NID> ":" <NSS>`

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"urn:foo:a123,456"`
`hasIdentifierResolveURI` |


## UUID

Sources:

- https://www.ietf.org/rfc/rfc4122.txt

Notes:

> The following is an example of the string representation of a UUID as
   a URN:
>
> urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6

- "The string representation of a UUID is fully compatible with the
      URN syntax."
- "The UUID format is 16 octets; some bits of the eight octet variant
   field specified below determine finer structure."
- "Since UUIDs are unique and persistent, they make excellent Uniform
   Resource Names.  The unique ability to generate a new UUID without a
   registration process allows for UUIDs to be one of the URNs with the
   lowest minting cost."
- UUIDs are commonly displayed as URNs (which are URIs)

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6`
`hasIdentifierResolveURI` |


## VIAF

I think this is the Virtual International Authority File

Sources:

- http://www.oclc.org/viaf.en.html


Notes:

- "The VIAF® (Virtual International Authority File) combines multiple name authority files into a single OCLC-hosted name authority service." (http://viaf.org/)
- Regex form: `([1-9]\d{1,8}|[1-9]\d{18,21}|)` (https://www.wikidata.org/wiki/Property:P214)

Recommendation:

Predicate                 | Object
--------------------------|--------------------------
`hasIdentifierValue`      | `"120062731"` (just numbers)
`hasIdentifierResolveURI` |
