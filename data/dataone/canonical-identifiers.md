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
- [Handle](#handle)
- [InfoURI](infouri)
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

### Related Work

http://bioinformatics.oxfordjournals.org/content/31/11/1875.full


## ARK

Source: https://confluence.ucop.edu/display/Curation/ARK (See: ARK Anatomy)

Notes:

- "The immutable, globally unique identifier follows the "ark:" label."
	- ark:/12025/654xz321/s3/f8.05v.tiff
- "When embedded in a URL, it is preceded by the protocol  ("http://") and name of a service that provides support for that ARK." e.g.
	- http://example.org/ark:/12025/654xz321/s3/f8.05v.tiff


General form: [http://NMAH/]ark:/NAAN/Name[Qualifier]

Recommend: ...


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


## Handle

TBD


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


## SICI

## SSN

## UPC

## URI

## URL

## URN

## VIAF
