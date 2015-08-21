---
author: Bryce Mecum
email: mecum@nceas.ucsb.edu
---

# Proposal for Handling DataOne People & Organizations

## Overview

The linked open data (LOD) graph for the datasets that exist in DataOne's network is nearly complete.
However, resources of type `glview:People` and `glview:Organization` are not represented as HTTP URIs but they need to be in order for our RDF graph to be an LOD RDF graph.
Instances of these two concepts present in DataOne datasets often are represented by the person or organization's name but do not come with existing LOD HTTP URIs we can re-use in our graph.
Therefore, new HTTP URIs will need to be created for instances of people and organizations that across datasets in the DataOne network.

Complicating this task, many instances of a person or organization present in the metadata may actually refer to the same person or organization.
When this is the case, we don't want to mint separate HTTP URIs for each instance of the same person or organization and instead we want to re-use existing HTTP URIs when appropriate.

The task of giving people and organizations HTTP URIs can be broken up into two parts:

1. Generate lists of unique people and organizations from DataOne
2. Mint new HTTP URIs for these resources

The above steps work if it's assumed the datasets present in DataOne are a finite set.
In reality, datasets are added to DataOne on a continuous basis and people and organizations in these new datasets may need to be associated with existing HTTP URIs or have new HTTP URIs created for them.
Therefore, a service that operates continuously is needed to ensure that the addition or update of datasets in the DataOne network will update nodes in the DataOne RDF graph.

To generate an initial RDF graph dump for the GeoLink project, the above steps will be performed on a snapshot of the DataOne datasets.
For the future, a service will need to be run continuously and either find existing HTTP URIs or mint new ones for datasets created or updated after the dump was created.

This proposal serves as a working document describing the approaches I intend to use to accomplish the above tasks.


## Finding unique people and organizations

Determining whether two instances of a person (i.e. the strings "B Mecum" and "Bryce Mecum") fundamentally refer to the same person is often referred to as record linkage or co-reference resolution.
There is no universal solution that can be expected to work in all situations and it may be the case that many instances cannot be confidently linked.
Two general approaches for record linkage might be used.

- Static matching (i.e. if name is the same, both records refer to the same thing)
- Machine learning (i.e. support vector machine on features such as Levenshtein distance)

I have experimented with both approaches and found value in both but I have also found limitations in both.
Static matching is simple to understand and implement but it can be hard to add enough flexibility to handle common problems such as typographical errors or abbreviations in names.
The machine learning approach is easy to implement but is a black box solution.
However, this approach offers a great deal of flexibility.
After experimenting, I think using both approaches will work better than using just one.

### Proposal

1. Get a set of datasets (either from a dump or from the CN's Solr index)
2. Pre-process those datasets
  - Generate derived fields (i.e. full name = salutation + givenName + surName)
3. Run a static matcher over the datasets with a set of rules (i.e. if full name and email is the same, it's the same person)
4. Train the machine learning algorithm on a custom set of training documents
  - I will hand-pick these from early runs of a poorly-trained classifier
5. Run the machine learning algorithm on the datasets
6. Analyze final output for quality
  - Detect false positives
  - Test how well the machine learning algorithm worked

A Python package [`dedupe`](https://github.com/datamade/dedupe) implements an advanced set of machine learning techniques designed specifically for record linkage and will be the used here.


## Minting new HTTP URIs

### URI Principles:

- It's okay if the same person has multiple HTTP URIs. We can later assert their sameness.
- Never assert two instances of a person or organization are the same person or organization (no false positives)
- URIs exist forever (URIs are never recycled or deleted)
- What those HTTP URIs resolve to may change
- This is especially import because the DataOne API may change but we don't want these URIs to ever change and we will want them to resolve to the active/latest API.
-

### Proposal

While it may seem reasonable to have nice HTTP URIs like `https://www.dataone.org/people/brycemecum`, it does not seem feasible given how many possible name collisions are possible, the vast number of non-ASCII characters present in names (i.e. 象形字), and the presence of datasets where only a last named was filled in.
Universally Unique Identifiers (UUIDs) will be used instead.


- People URIs at `https://www.dataone.org/person/`
  - i.e. `https://www.dataone.org/person/123e4567-e89b-12d3-a456-426655440000`
- Organization URIs at `https://www.dataone.org/organization/`
  - i.e. `https://www.dataone.org/organization/123e4567-e89b-12d3-a456-426655440000`


UUIDs will be generated as UUID 4 (random) and checked for collision with existing UUIDs prior to establishing new HTTP URIs.

Aside: DataOne already has some people HTTP URIs, e.g. https://www.dataone.org/dataone_leadership_team/matthew-jones but I don't think this format (org/person) needs to be used here.


## The Service

The service needs to run continuously and know about two things. The first is what datasets are new or updated since the last graph was created.
This can be done with a Solr query like:

```{text}
https://cn.dataone.org/cn/v1/query/solr/?q=dateUploaded:[2015-05-30T23:21:15.567Z%20TO%202015-08-21T00:00:00.0Z]
```

- [ ] @mbjones: I can't seem to find out if dateUploaded is a safe way to assess which documents are updated/created since a certain datetime.

In the above query, the first datetime is the last datetime the graph was updated, which the service remembers, and the second datetime is the current time.

The second thing the service needs to know about is the existing set of people and organization HTTP URIs.

And with this information, the service needs to do three things:

1. Mint new HTTP URIs as necessary
  - Create the URI itself
  - Register that URI with some other service responsible for resolving it
2. Update the set of people and organizations HTTP URIs
3. Update the latest DataOne RDF graph
  - Create new people and organization nodes for new people and organizations
  - Update information about existing people and organizations

Updating existing people and organizations will involve updating both `glview:People` and `glview:Organization` resources as well as `glview:Dataset` resources.

Existing services on DataOne are Java programs but the language of the current implementation is Pyton. This can be changed.



## Notes
Use of solr dateModified??? 2013-06-11T06:11:23.217Z




dateSysMetadataModified (Solr: dateModified)
Type: Types.xs.dateTime

Date and time (UTC) that this system metadata record was last modified in the DataONE system. This is the same timestamp as dateUploaded until the system metadata is further modified. The Member Node must set this optional field when it receives the system metadata document from a client.




dateUploaded (Solr: dateUploaded)
Type: Types.xs.dateTime

Date and time (UTC) that the object was uploaded into the DataONE system, which is typically the time that the object is first created on a Member Node using the MNStorage.create() operation. Note this is independent of the publication or release date of the object. The Member Node must set this optional field when it receives the system metadata document from a client.
