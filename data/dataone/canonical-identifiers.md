# Canonical Identifiers

Identifiers to concepts beyond the scope of GeoLink (e.g. DOI, ORCID) are going to be prevalent in the GeoLink graph. Each identifier may have multiple serializations and it would be beneficial if we adopted one per identifier. See #51 for more.

For some identifiers, finding a single best form for use in LOD graphs may be ambiguous. However, it is not necessary that we use the best form (if it may exist) but that we use a single form consistently throughout all of our LOD graphs.

Here's what I did:

- Tried to find a best source of information for each identifier and included a link if I found one.
- Tried to find an example usage of the identifier in the wild
- Tried to make the distinction between the identifier itself and the resolution method for that identifier
- Tried to make the distinction between use cases and make sure we had the best form for use in an LOD graph.
- Tried to find an endpoint that responds with RDF/XML or some other serialization of triples

Identifiers:

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
- [VIAF](#viaf)


### A Note on Web-Resolvable Identifiers

It might be really nice to ensure we take a similar approach for all identifiers that have resolution services (e.g. DOI, Handle). This gets tricky because a number of services use identifiers of this form but they recommend slightly different use patterns.

For example, DOI suggests using http://doi.org/{DOI} while FundRef uses http://dx.doi.org/{DOI} as their identifiers. It may be confusing to store DOIs in different forms but in a way, a DOI that is used as a FundRef DOI Is more of a 'FundRef DOI' rather than an 'DOI DOI'.


### Machine Form vs. Display Form vs. Web-Resolvable Form

As mentioned above, many identifiers come with some form of resolution service which can be used to retrieve the entity the identifier refers to.
In some cases, an identifier may be resolved using numerous resolution services (e.g., ARK, DOI) -- some of all of which may cease to exist in the future -- while the identifier itself is considered permanent.
For embedding identifiers into RDF, it would be good to take care to use the right form of the identifier (if numerous exist).
For each identifier, information on the forms an identifier may take is recorded and, if the authority for the identifier recommends specific forms of its identifiers for different uses (e.g., use in RDF, display on a website), those recommendations will be documented.

Three terms will be used to describe these forms:

- Machine Form: The best form to use when serializing and storing the identifier
- Display Form: The best form to use when displaying in print or on the web
- Resolvable Form: Whether the identifier has a web resolvable form and what that form looks like


### Related Work

http://bioinformatics.oxfordjournals.org/content/31/11/1875.full


## ARK

Source: https://confluence.ucop.edu/display/Curation/ARK (See: ARK Anatomy)

Notes:

- "The immutable, globally unique identifier follows the "ark:" label."
	- ark:/12025/654xz321/s3/f8.05v.tiff
- "When embedded in a URL, it is preceded by the protocol  ("http://") and name of a service that provides support for that ARK." e.g.
	- http://example.org/ark:/12025/654xz321/s3/f8.05v.tiff


Recommendation:

- Machine Form? `ark:/12025/654xz321/s3/f8.05v.tiff` or `http://example.org/ark:/12025/654xz321/s3/f8.05v.tiff`
- Display Form? Unknown
- Resolvable Form? Yes (`http://example.org/ark:/12025/654xz321/s3/f8.05v.tiff`)


## arXiv

Sources:
- http://arxiv.org/help/arxiv_identifier_for_services
- http://arxiv.org/help/faq/references
- http://arxiv.org/help/arxiv_identifier


Notes:

- arXiv changes their format over time and article identifiers are not updated.
- "The form of arXiv identifiers for new articles changed on 1 April 2007, and the number of digits in the sequence number changed again on 1 January 2015. All existing articles retain their identifiers."
- arXiv uses arXiv:hep-th/9901001v2 to link to http://arxiv.org/abs/hep-th/9901001v2

Example: arXiv:1207.2147
General form: arXiv:YYMM.number

Recommend: ...


## DAI

Source: https://wiki.surfnet.nl/display/standards/DAI

Notes:

- "The DAI (or PPN) contains 9 to 10 characters. The first 8 to 9 characters are numbers. The last (9th or 10th) character is a control character. The control character is a modulus 11 check digit, like in the ISBN."
- "The DAI is the number after the string info:eu-repo/dai/nl/ . A DAI is a number like 123456785. The last character is a MOD11 check-digit.
- The string: info:eu-repo/dai/nl/ is just an authority namespace, telling the user or machine that the number is a DAI originating from the Netherlands."
- So the DAI is 9-10 chars. If it's URI-ified, it'll have something like 'info:eu-repo/dai/nl/' prepended to it.
- I found an example of one on narcis.nl: info:eu-repo/dai/nl/275853993

Recommend: ...


## DOI

Notes:

> To resolve a DOI via a standard web hyperlink, the DOI name itself should be appended to the address for the proxy server.
> 	EXAMPLE
> 	The DOI name "10.1006/jmbi.1998.2354" would be made an actionable link as "http://doi.org/10.1006/jmbi.1998.2354".
>
> Source: http://www.doi.org/doi_handbook/2_Numbering.html

> So while it may be awkward, we recommend some convention of showing both the plain DOI name and a way to resolve it online (a shorthand way of saying "the DOI name for this article is 10.1002/prot.999 and current information may be found on the web through http://doi.org/10.1002/prot.999" or "...available via http://doi.org/...".

- DOI doesn't promise the resolve URL will work forever so they recommend the above.
- DOI.org prefers resolving at doi.org/ instad of dx.doi.org, even though the maintain dx.doi.org. (Source: http://www.doi.org/factsheets/DOIProxy.html)

- CrossRef is much more didactic about what to do at http://www.crossref.org/02publishers/doi_display_guidelines.html where they recommend always using the dx.doi.org/ URL when (among other things) "Anywhere users are directed to a permanent, stable, or persistent link to the content".

- DOIs are meant to be resolvable on the web. (Source: http://www.doi.org/doi_handbook/1_Introduction.html)

Resolve URL: http://dx.doi.org/10.1093%2Fnar%2Fgks1195

Recommend: Use http://doi.org resolve URL, e.g. 'http://doi.org/10.1006/jmbi.1998.2354' for the identifier.


## EAN13

Source: http://www.gs1.org/barcodes/ean-upc

General form: 13-digit (12 data, 1 check) number

Recommend: ...


## EISSN

Sources:

- http://www.issn.org/understanding-the-issn/what-is-an-issn/
- http://www.issn.org/understanding-the-issn/assignment-rules/the-issn-for-electronic-media/

Notes:

> What form does an ISSN take?
> The ISSN takes the form of the acronym ISSN followed by two groups of four digits, separated by a hyphen. The eighth digit is a check digit calculated according to a modulus 11 algorithm on the basis of the 7 preceding digits; this eighth control digit may be an “X” if the result of the computing is equal to “10”, in order to avoid any ambiguity.
>
> e. g.:
>
> ISSN 0317-8471
> ISSN 1050-124X

- I just found this on CrossRef: https://api.crossref.org/v1/works/http://dx.doi.org/10.3390/e17041701. The ISSN is given as just '1099-4300'. Maybe that's the best way.

Recommend: `0317-8471` because the ISSN part is redundant and I've seen a use in the wild (see above) that omits the 'ISSN' before the numbers.


## FundRef

Source: http://www.crossref.org/fundref/

Notes:

- FundRef offers up its own identiifers, e.g. 501100004802, but these do not appear to be FundRef identifiers but just internal identifiers instead. e.g.
http://search.crossref.org/fundref?q=501100004802
- FundRef is just a mapping service between the funder and their canonical name. For example, FundRef maintains the mapping 'http://dx.doi.org/10.13039/100000001' to `National Science Foundation`. All the mappings in their system uses the dx.doi base URL.
- When you resolve a FundRef DOI, they report back with an `id` in the form of 'http://dx.doi.org/10.13039/100000001'.

Recommend: Store as FundRef stores them: 'http://dx.doi.org/10.13039/100000001'


## GVP

Sources:

- No good source describing identifier structure/representation.
- http://volcano.si.edu/gvp_vnums.cfm
- http://volcano.si.edu/list_volcano_holocene.cfm

About:

Smithsonian's Global Volcanism Program (GVP) announces new and permanent
unique identifiers (Volcano Numbers, or VNums) for volcanoes documented in
the Volcanoes of the World (VOTW) database maintained by GVP and accessible
at www.volcano.si.edu.

Examples:

- GVP:210010
- http://volcano.si.edu/volcano.cfm?vn=210010


Recommend: GVP:210010


## Handle

TBD

## IGSN

Sources:

- http://www.geosamples.org/igsnabout
- http://www.geosamples.org/aboutigsn

About:

IGSN stands for *International Geo Sample Number*. The IGSN is 9-digit
alphanumeric code that uniquely identifies samples from our natural
environment and related sampling features. You can get an IGSN for your
sample by registering it in the System for Earth Sample Registration SESAR.

Notes:

- The IGSN is 9-digit alphanumeric code that uniquely identifies samples from our natural environment and related sampling features.
- IGSN's can have URIs, though not consistently: http://www.geosamples.org/profile?igsn=IECUR001E
- The IGSN follows the syntax of the URN (Uniform Resource Name) which is composed of a ‘Namespace Identifier' (NID), a unique, short string, and the ‘Namespace Specific String’ (NSS).
- "...the first five digits of the IGSN represent a name space (a unique user code) that uniquely identifies the person or institution that registers the sample."
- "The last 4 digits of the IGSN are a random string of alphanumeric characters (0-9, A-Z)."
- "IGSN namespaces that were obtained before July 2014 may have three digit namespaces followed by a random string of 6 alphanumeric characters (e.g. examples #1 and # 2 above). For more information see http://www.geosamples.org/news/namespacechanges."

Examples:

- IGSN:HRV003M16
- IGSN: IECUR001E (has extra space)

Recommend:

- IGSN:HRV003M16 (9 digits)


## IMA

Sources:

- http://www.ima-mineralogy.org/Minlist.htm

About:

International Mineralogical Association (IMA) publish the list contains
names and data for minerals which have been approved, discredited,
redefined and renamed and is the new revised master list of all
IMA-approved and grandfathered (i.e. inherited from before 1960) minerals.


Examples:

- IMA:2014-028
- IMA1975-013 (on http://rruff.info/ima/)
- 'No. 2014-103' in print.

Notes:

- "The continuing integrity of the (web-based) IMA mineral list will be maintained by the IMA outreach committee, and additional features are being developed by the RRUFF™ Project."
- It does not publish the URIs that speak RDF

Recommend: IMA:2014-028


## InfoURI

Source: http://info-uri.info/registry/docs/misc/faq.html

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
>
> 1. Normalize the case of the "scheme" component to be lowercase.
> 2. Normalize the case of the "namespace" component to be lowercase.
> 3. Unescape all unreserved %-escaped characters in the "namespace" and "identifier" components.
> 4. Normalize the case of any %-escaped characters in the "namespace" and "identifier" components to be uppercase.
> 5. The subsequent namespace-specific normalization steps may be applied:
> 6. Normalize the case of the "identifier" component as per any rules that may be recorded in the Registry.
> 7. Normalize any punctuation characters in the "identifier" component as per any rules that may be recorded in the Registry.


Recommend: Use 'info:pii/S0888-7543(02)96852-7'


## InterRidge

Sources:

- http://vents-data.interridge.org/sites/vents-data.interridge.org/files/InterRidge_Vents_Database_Version3.1_documentation.pdf
- http://vents-data.interridge.org/about_the_database

About:

The InterRidge Global Database of Active Submarine Hydrothermal Vent
Fields, hereafter referred to as the “InterRidge Vents Database,” is to
provide a comprehensive list of active and inferred active (unconfirmed)
submarine hydrothermal vent fields for use in academic research and
education.

Examples:

- InterRidge:13-n-ridge-site
- http://vents-data.interridge.org/ventfield/13-n-ridge-site

Notes:

- It speaks RDF from version 3, and provide SPARQL endpoint http://vents-data.interridge.org/sparql
- "In the vents database, the URIs are comprised of the site
namespace, which should be persistent ... and the node ID (nid) for each vent field (i.e., the
node ID for each vent field is effectively the unique identifier for that vent field) or unique name of
the vent field using path alias, e.g., Mariner is http://irvents-new3.whoi.edu/node/1001 and
http://irvents-new3.whoi.edu/ventfield/mariner."


Recommend: InterRidge:13-n-ridge-site


## ISBN

Source: https://www.isbn-international.org/sites/default/files/ISBN%20Manual%202012%20-corr.pdf

- "When printed, the ISBN is always preceded by the letters “ISBN”."
	- e.g. ISBN 978-0-571-08989-5

Recommend: '978-0-571-08989-5'


## ISNI

- ISNI has publicly committed to implementing URIs that speak RDF (Source: https://lists.w3.org/Archives/Public/public-lod/2013Dec/0047.html).

Examples:

- ISNI 0000 0003 9591 6013
- ISN:0000000395916013
- http://isni.org/isni/0000000124514311

Notes:

- For http://isni.org/isni/ URLs, ISNI doesn't make it very clear what that service is or how committed they are to keeping it up.

Recommend: '0000000395916013'


## ISSN

Source: http://www.issn.org/understanding-the-issn/assignment-rules/issn-manual/

Notes:

- 'An ISSN consists of eight digits. These are the Arabic numerals 0 to 9, except that an upper case X can sometimes occur in the final position as a check digit.'

Recommend: '15626865'


## ISSN-L

See above (ISSN)

Recommend: '17487188'


## ISTC

Source: http://www.istc-international.org/html/about_structure_syntax.aspx

Recommend: 0A9200212B4A1057
- Strip spaces and hyphen as they are not part of the ISTC.


## JST

Not sure on this one.


## LSID

Source: file:///Users/mecum/Downloads/dtc-04-05-01.pdf

Notes:

- 'Life Sciences Identifiers are case-insensitive for the first three portions of the identifier ("URN", "LSID", authority identification). The remainder of the identifier (namespace identification, object identification, revision identification) is case sensitive.'

Recommend: 'urn:lsid:XXXX'
- Downcase urn and lsid, but leave the rest in-tact.

## National Insurance Number

Source: http://www.hmrc.gov.uk/manuals/nimmanual/NIM39110.htm

Recommend: 'QQ123456A'


## NIHMSID

TBD


# OpenID

Notes:

- Under OpenID Auth 1.1 (http://openid.net/specs/openid-authentication-1_1.html), OpenID Identifiers are just URLs and follow the same rules.

Recommend: Format as URLs.


# ORCID

Notes:

- ORCIDs are usually serialized as either:
	- http://orcid.org/0000-0001-9923-4648 or
	- 0000-0001-9923-4648
- ORCID responds to RDF/XML if you send an accept header to them (redirects to something like https://pub.orcid.org/experimental_rdf_v1/0000-0001-9923-4648).

Recommend: http://orcid.org/0000-0001-9923-4648


## PII

Sources:

- http://web.archive.org/web/20031013073003/
- http://www.elsevier.nl/inca/homepage/about/pii/

General forms:

- PII: Sxxxx-xxxx(yy)iiiii-d
- B x-xxx-xxxxx-x/iiiii-d

Recommend: Just store the 17 characters (no hyphens, slashes).


## PMCID

These need to be distinguished from PMIDs. That is done by prepending PMC to the ID, e.g. PMC3531190.

Resolve URL: http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3531190/

Recommend: 'PMC3531190' unless we come to a consensus about using resolve URIs where possible.


## PMID

These appear to just be a string of numbers, e.g. 23193287.

Resolve URL: http://www.ncbi.nlm.nih.gov/pubmed/23193287

Recommend: '23193287'


## PURL

Source: https://sites.google.com/site/persistenturls/

All PURLs are URLs.

Recommend: Follow URL pattern.

## ResearcherID

ResearcherID are commonly serialized and shared as X-XXXX-XXXX

Recommend: 'X-XXXX-XXXX'

## SCAR

Sources:

- No good source describing identifier structure/representation.
- https://www1.data.antarctica.gov.au/aadc/gaz/scar/information.cfm

About:

The Scientific Committee on Antarctic Research (SCAR),  through its
recommendations, expresses the hope that the present effort will contribute
to the adoption in Antarctica of the general principle of 'one name per
feature' by all Antarctic place naming authorities.

Examples:

- SCAR:883

Notes:

- It does not publish URIs that speak RDF

Recommend: SCAR:883


## SICI

## SSN

## UPC

## URI

## URL

## URN

## VIAF
