---
author: Bryce Mecum
email: mecum@nceas.ucsb.edu
---

# DataOne Graph Service Proposal

## Contents

- [DataOne Graph Service Proposal](#dataone-graph-service-proposal)
	- [Contents](#contents)
	- [Overview](#overview)
	- [Timeline](#timeline)
	- [Graph Service](#graph-service)
		- [How the Graph Service Operates](#how-the-graph-service-operates)
		- [Issues](#issues)
	- [Matching People and Organizations](#matching-people-and-organizations)
		- [Minting URIs](#minting-uris)
		- [Minting Principles:](#minting-principles)
		- [DataOne Integration](#dataone-integration)
	- [Matching DataOne Accounts](#matching-dataone-accounts)
	- [Notes](#notes)
		- [RDF Graph Generation Notes](#rdf-graph-generation-notes)


## Overview

For DataOne's part in GeoLink, we are producing an RDF graph of the datasets present on DataOne and this graph must be updated as datasets are added to the DataOne network.
The graph will contain information on datasets, which contain information on resources people, organizations, measurements, etc.
The DataOne Graph Service will use a triple store to store the triples for all datasets and will be run periodically to scan for datasets that have been revised or added since the last time the graph was created.
It will then create triples for these updated datasets and update the graph.

The graph we produce should follow best practices for linked open data (LOD).
Datasets in the DataOne network already come with their own HTTP URIs but people and organizations do not.

It would be simple enough to mint unique URIs for each and every instance of a person or organization in the DataOne network and store those in the graph.
However, it would add a lot of value back into DataOne if we could somehow find out which of these instances of people and organizations are actually the same and link them and their datasets together.
We could then link a person's datasets to their DataOne accounts and produce more useful user portal pages.

So when we extract people and organizations from a new dataset, we will need to attempt to find a match for them in the existing graph.
When a match is found (the rules for a match are described below), the existing URI will be re-used and any information found in the new dataset about that person's name, email, affiliations, etc. will be added to the graph.
When no match is found, a new URI will be minted for that person or organization.

Finally, the service should integrate back into DataOne to match DataOne accounts with the account holder's datasets.

This document is thus broken down into two main parts:

- The DataOne Graph Service
- Minting and re-using people and organization URIs in the graph
- Integration with DataOne

with the ultimate goal being to produce an RDF graph of datasets on DataOne.


## Timeline

Creating the graph is broken down into sequential deliverables:

- [x] Create initial LOD graph of existing DataOne datasets: September 4
- [x] Create service which pulls new metadata and integrates it into the graph:
  September 18
- [ ] Integrate with DataOne V2 API: TBD


## Graph Service

The graph service needs to run continuously and know what datasets are new or were revised since the last graph was created.
This can be done with a Solr query like:

```{text}
https://cn.dataone.org/cn/v1/query/solr/?q=dateUploaded:[2015-05-30T23:21:15.567Z%20TO%202015-08-21T00:00:00.0Z]
```

In the above query, the first datetime is the last datetime the graph was updated, which the service needs to store, and the second datetime is the current datetime. Note the 'fields' and other query parameters have been omitted for clarity.
The above query will return zero or more PIDs that need processing and the graph service will then process them.

Existing services on DataOne are Java programs but the language of the current implementation is Python. This can be changed.

The current implementation of the Python script `get_new_datsets.py` relies in three separate [Fuseki](https://jena.apache.org/documentation/serving_data/) stores (which is not ideal but works) running on the host machine.
The required PIDs are processed, their triples are added to the graph, and a SPARQL CONSTRUCT statements is used to export the graph into a Turtle file, one for each of datasets, people, and organizations.

Because the graph of datasets needs to be kept up-to-date, triples will need to be added and/or removed over time in order to keep the RDF graph in sync with datasets in the network.
There is a chance here to integrate with existing infrastructure in DataOne and this may be the best way to do things.
In the existing system, when a dataset is added to a member node, a series of actions may be spun off, such as generating system metadata and replicating scientific metadata and the data itself to other nodes.
It's easy to imagine kicking off another action to direct another piece of DataOne infrastructure to analyze the newly-added dataset for information relevant to the RDF graph of datasets.

The alternative to this integrated service is to develop separate infrastructure which polls a coordinating node at regular intervals and initiates the necessary steps to update the RDF graph of datasets.
This is the current approach.

### How the Graph Service Operates

- The service is started
- Query the CN Solr index for new dataset
- For each dataset:
  - If the dataset already exists, delete all triples about it from the graph
  - Retrieve the scientific metadata for the PID from a cache or from the CN
    - Extract people and organization information from the scientific metadata
      - Re-use or mint new URIs for them either from
      - Add information about them from the current dataset
  - Extract dataset information from the Solr index result (title, digital objects, etc)
  - Retrieve each digital object for the dataset
  - Add all triples about the dataset to the graph


### Issues

What to do about people URIs where we only have the name?

When we change the information we extract from datasets, we will have to re-process datasets.
When a dataset is re-processed, we remove all the triples we added the last time the dataset was processed and then add them again with the (possibly) updated information.
People without sufficient distinguishing information (i.e., without emails addresses) will always trigger the minting of a new URI even though we minted them a new URI the last time their document was processed.
This is because we never remove knowledge about a person (like their first name) from the graph when we remove triples for a dataset prior to re-processing.
The only knowledge we remove is that they are the creator of the given dataset which is easy to remove.

Below is a worked example with TTL syntax showing what happens under the current system:

First, Dataset X is added, which contains person Jane Doe.
The people graph looks like this:

```{ttl}
<https://dataone.org/person/urn:uri:someuuid>
        <http://schema.geolink.org/dev/view/isCreatorOf>
                <https://cn.dataone.org/cn/v1/resolve/X> ;
        <http://schema.geolink.org/dev/view/nameFamily>
                "Doe" ;
        <http://schema.geolink.org/dev/view/nameFull>
                "Jane Doe" ;
        <http://schema.geolink.org/dev/view/nameGiven>
                "Jane" .
```

All is well. Then we re-process dataset X because it is updated. We remove the `isCreatorOf` triple from Jane Doe.

```{ttl}
<https://dataone.org/person/urn:uri:someuuid>
        <http://schema.geolink.org/dev/view/nameFamily>
                "Doe" ;
        <http://schema.geolink.org/dev/view/nameFull>
                "Jane Doe" ;
        <http://schema.geolink.org/dev/view/nameGiven>
                "Jane" .
```

And continue re-processing.
Because we can't be sure if Jane Doe with URI `<https://dataone.org/person/urn:uri:someuuid>` is the same Jane Doe as is in dataset X, we mint a new URI and end up with:

```{ttl}
<https://dataone.org/person/urn:uri:someuuid>
        <http://schema.geolink.org/dev/view/nameFamily>
                "Doe" ;
        <http://schema.geolink.org/dev/view/nameFull>
                "Jane Doe" ;
        <http://schema.geolink.org/dev/view/nameGiven>
                "Jane" .

<https://dataone.org/person/urn:uri:another_uuid>
        <http://schema.geolink.org/dev/view/isCreatorOf>
                <https://cn.dataone.org/cn/v1/resolve/X> ;
        <http://schema.geolink.org/dev/view/nameFamily>
                "Doe" ;
        <http://schema.geolink.org/dev/view/nameFull>
                "Jane Doe" ;
        <http://schema.geolink.org/dev/view/nameGiven>
                "Jane" .
```

If we think just about the knowledge stored in this graph, it would seem reasonable to simply re-use the first URI for Jane Doe given that it contains no `isCreatorOf` triples.
This is because the first URI we minted no longer contains any `isCreatorOf` triples so we wouldn't be saying anything inconsistent.
However, this might not be a good idea if we consider that triples may have been created outside of our graph using the first URI and that re-using the URI might result in assertions that a different person than we say created this dataset, either in our graph or another.
I'm not sure if this is really an issue.

Solutions I can see at this time are to either accept this reality and aim to never re-process datasets manually or  introduce a provenance graph for document processing that will allow us to delete these problem triples.
I recommend accepting the reality and moving on, aiming to limit manual re-processing (this should be easy).
This would mean accepting that the people graph might contain URIs that aren't `isCreatorOf` for any datasets.


## Matching People and Organizations

Determining whether two instances of a person (i.e. the strings "B Mecum" and "Bryce Mecum") refer to the same person is often referred to as record linkage or co-reference resolution.
There is no universal solution that can be expected to work in all situations and it may be the case that many instances cannot be confidently linked.
Two general approaches for record linkage might be used.

- Static matching (i.e. if name is the same, both records refer to the same thing)
- Machine learning (i.e. support vector machine on features such as Levenshtein distance)

I have experimented with both approaches and found value in both but I have also found limitations in both.
Static matching is simple to understand and implement but it can be hard to add enough flexibility to handle common problems such as typographical errors or abbreviations in names.
The machine learning approach is easy to implement but is a black box solution.
However, this approach offers a great deal of flexibility.
For the initial implementation of the tool that performs this task, only static matching will be used.
The machine learning approach may be re-visited later on for use within this workflow or as a separate workflow which tries to establish linkages between existing HTTP URIs.


### Minting URIs

### Minting Principles:

- It's okay if the same person has multiple HTTP URIs. We can later assert their sameness with something like `owl:sameAs`.
- Never assert two instances of a person or organization are the same person or organization (no false positives)
- URIs exist forever (URIs are never recycled or deleted)
- What those HTTP URIs resolve to may change
  - This is especially import because the DataOne API may change but we don't want these URIs to ever change and we will want them to resolve to the active/latest API.

Proposed Approach:

While it may seem reasonable to take a person in metadata record with the full
name 'Bryce Mecum' and mint a nice HTTP URI like
`https://www.dataone.org/people/brycemecum`, it is not feasible to do this for
every person or organization given how many possible name collisions are
possible, the vast number of non-ASCII characters present in names (i.e. 象形字),
and the presence of datasets where only a last named was filled in. Universally
Unique Identifiers (UUIDs) are a potential option. - People URIs at
`https://dataone.org/person/` - i.e.
`https://dataone.org/person/urn:uuid:123e4567-e89b-12d3-a456-426655440000`

- Organization URIs at `https://dataone.org/organization/`
  - i.e. `https://dataone.org/organization/urn:uuid:123e4567-e89b-12d3-a456-426655440000`

UUIDs would be generated as UUID 4 (random) and checked for collision with existing UUIDs prior to establishing new HTTP URIs. Note that the above URIs use the `urn:uunid` prefix before the UUID itself. This is a workaround for the case when a UUID begins with a number.

DataOne manages a number of authentication services (See below: [Matching DataOne Accounts](#matching-dataone-accounts)).
It is possible that, in the future, users from these services will have their own, human-readable HTTP URIs (like [http://dataone.org/people/brycemecum](http://dataone.org/people/brycemecum)).
These URIs would be vastly preferable to a UUID4-based URI and should be used instead.
This decision would be made prior to minting a new HTTP URI for an instance of a person in a dataset and would require some form of resolution between the authentication service and the graph generation service.

For some instances of people in datasets, it may be possible to make a highly confident match between the instance of that person and a person in an authentication system.
For example, if the first name, last name, and email are the same in both systems, it is very likely that both instances refer to the same person.
For instances of people in datasets without such identifying information, a match with a lower degree of certainty could be made which might still be useful to the person.

Summary:

- For most people and organizations, mint and maintain a UUID4-based URI.
- If we can match with 100% certainty to a DataOne account (i.e. both have an ORCID), re-use their user account portal URI (e.g. /people/brycemecum).
- If we cannot match them with 100% confidence but have more than 0% confidence, assert a property named something like `:couldBeSameAs`.


### DataOne Integration

Regarding #4 (above), when new HTTP URIs are created for a person or organization, that person or organization may exist in another system we operate.
Ideally, at the time of creating a new HTTP URI also, we would find out of the person or organization we're creating a new HTTP URI for exists in other systems and make the appropriate associations.
The key benefit of doing this would not just be directly linking, for example, someone in LDAP with their GeoLink HTTP URI but, instead, linking a someone in LDAP with datasets they created.
In creating these linkages, it's important that no linkages that would result in changes to access privileges are made unless those changes are done through a secure system.
For example, you wouldn't want to parse an EML document, find a person in LDAP with similar name, and allow that person to delete that dataset.
It would be good to present linkages we have confidence in to the authenticated user (e.g. on LDAP) and allow them to confirm or deny sameness.

Once the linkages are made, visiting a person's user account page (e.g. [http://dataone.org/people/brycemecum](http://dataone.org/people/brycemecum)) would show both datasets that certainly reference the user as well as datasets that may reference the user.
These linkages could be confirmed or denied by the logging-in user.
Linkages made in this way would still be imperfect because a user could mistakenly claim someone else's data when the data weren't uploaded with sufficiently unique identifying information.
But if, for example, the dataset contained a DataOne URI or an ORCID and the user account had one of these identifiers, then the match between the user and the reference to a person in the dataset would be essentially certain (absent typos).

In the above scenario, a user account might contain hierarchical person information such as:
- [http://dataone.org/people/brycemecum](http://dataone.org/people/brycemecum) [an authenticated account]
  - matches: [http://dataone.org/people/123e4567-e89b-12d3-a456-426655440000](http://dataone.org/people/123e4567-e89b-12d3-a456-426655440000) [a possible match]
  - hasAccount: CN=Bryce Mecum A81283,O=Google,C=US,DC=cilogon,DC=org [an authenticated match]
  - hasConfirmedMatch: [https://dataone.org/person/123e4567-e89b-12d3-a456-426655440549](https://dataone.org/person/123e4567-e89b-12d3-a456-426655440549) [user indicated this is them]

And from this hierarchical set of user information, we could link in datasets attributed to these people.


## Matching DataOne Accounts

Performing this record linkage activity for GeoLink project could be considered useful in and of itself. However, we have the opportunity to make this even more useful by integrating it with work already being done at DataOne on linking authenticated user accounts together. Users who directly interact with the DataOne network may have records in one or more authentication systems (e.g. LDAP) operated by DataOne. Any particular person, by having interacted with DataOne in multiple ways over time, may exist in multiple authentication systems and, therefore, have multiple accounts associated with themselves. DataOne is working on a manual tool for users to bundle their multiple accounts together under a single account. This record linkage activity within DataOne is useful because DataOne wants to be able to link scholarly work to people and having multiple accounts per person could splinter their scholarly work across multiple accounts. As for a person's datasets, they are often associated with a single account by virtue of the way metadata/data are uploaded and won't be immediately linked to that user's accounts in other authentication systems. This could change in the future if tools for uploading data to DataOne change but it remains a problem for now. Without the link between authentication systems, a person may not be able to find all of the datasets they have uploaded over time which would lessen the utility of what DataOne is offering.

The previous activity only solves the problem of linking users to their datasets for users that directly interact with the DataOne authentication systems. This is a very small subset of all the people and organizations who exist within metadata records. The work being done in the GeoLink project nicely fills this gap because we are already harvesting instances of people and organizations from the metadata in the DataOne network.

Instances of people and organizations we find within metadata records can be matched to people and organizations within the DataOne datasets and the datasets can then be linked to user accounts. However, the information about people and organizations that is present in metadata is often vague and may not provide enough information to conclusively match two instances of a person or organization together and/or match them to an DataOne account. Most metadata does not contain established, globally unique identifiers (such as ORCIDs) so the matching must be done on information such as name, organization, email, etc. Because this type of linkage is only a guess, it cannot be asserted that we are 100% sure the DataOne user with a name (e.g. Bryce Mecum) is the same person as the person who uploaded a dataset and filled in just their full name (e.g. Bryce Mecum).

In these cases where the match is not certain, we will use a different semantic concept (e.g. `mayBeTheSameAs`) than when we have 100% certain (as with ORCIDs) which could be done using `owl:sameAs`.

See [Service Integration](#service-integration) for a description of how the linkage between DataOne accounts and instances of people and organizations could be done.


## Notes
Use of solr dateModified

dateSysMetadataModified (Solr: dateModified) Type: Types.xs.dateTime

Date and time (UTC) that this system metadata record was last modified in the DataONE system. This is the same timestamp as dateUploaded until the system metadata is further modified. The Member Node must set this optional field when it receives the system metadata document from a client.

dateUploaded (Solr: dateUploaded) Type: Types.xs.dateTime

Date and time (UTC) that the object was uploaded into the DataONE system, which is typically the time that the object is first created on a Member Node using the MNStorage.create() operation. Note this is independent of the publication or release date of the object. The Member Node must set this optional field when it receives the system metadata document from a client.

### RDF Graph Generation Notes

Public vs Private Datasets

The dump being processed to create the initial RDF graph contains some datasets
that are private. We're still harvesting the information for people and
organizations but we aren't linking in their document identifiers.

How the deduplication is working

The following organizations will not be deduped with the current approach so they
will each get their own URI.

- Taiwan  Forestry Research Institute
- Taiwan Forest Research Institute
- Taiwan Forestry Institute
- Taiwan Forestry Research Institute
- Taiwan forestry research institute
- TaiwanForestry Research Institute

A possible solution might be to (1) remove double-spaces from strings and/or (2)
remove all whitespace and downcasing strings when comparing. I'm not sure how
the last part would work in terms of choosing a canonical form of the
organization when there are duplicates like the above.
