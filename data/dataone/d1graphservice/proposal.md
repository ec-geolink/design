---
author: Bryce Mecum
email: mecum@nceas.ucsb.edu
---

# Proposal for Handling DataOne People & Organizations

## Contents

- [Overview](#overview)
- [Timeline](#timeline)
- [Finding unique people and organizations](#finding-unique-people-and-organizations)
- [Minting new HTTP URIs](#minting-new-http-uris)
- [Matching DataOne Accounts](#matching-dataone-accounts)
- [Graph Service](#graph-service)
- [Notes](#notes)


## Overview

The linked open data (LOD) graph for the datasets that exist in DataOne's network is nearly complete. However, resources of type `glview:People` and `glview:Organization` are not represented as HTTP URIs but they need to be in order for our RDF graph to be an LOD RDF graph. Instances of these two concepts present in DataOne datasets often are represented by the person or organization's name but do not come with existing HTTP URIs we can re-use in our graph. Therefore, new HTTP URIs will need to be created for instances of people and organizations that across datasets in the DataOne network.

Complicating this task, many instances of a person or organization present in the metadata may actually refer to the same person or organization. When this is the case, we don't want to mint separate HTTP URIs for each instance of the same person or organization and instead we want to re-use existing HTTP URIs when appropriate.

The task of giving existing people and organizations HTTP URIs can be broken up into two parts:
1. Generate lists of unique people and organizations from DataOne
2. Mint new HTTP URIs for these resources or re-use existing URIs from other systems (e.g. DataOne portal pages)

The above steps assume the datasets present in DataOne are a finite set. In reality, datasets are added to DataOne on a continuous basis and people and organizations in these new datasets may need to be associated with existing HTTP URIs or have new HTTP URIs created for them. Therefore, a service that operates continuously is needed to ensure that the addition or update of datasets in the DataOne network will update nodes in the DataOne RDF graph.

To generate an initial RDF graph dump for the GeoLink project, the above steps will be performed on a snapshot of the DataOne datasets. For the future, a service will need to be run continuously and either find existing HTTP URIs or mint new ones for datasets created or updated after the dump was created.

This proposal serves as a working document describing the approach to accomplish the above tasks.

## Timeline

Creating the pieces outlined above will take a great deal of work as a whole but can be broken down into sequential deliverables with an attached timeline.
- Create initial LOD graph of existing DataOne datasets: September 4: DONE
- Create service which pulls new metadata and integrates it into the graph: September 18
- Integrate with DataOne V2 API: TBD


## Finding unique people and organizations

Determining whether two instances of a person (i.e. the strings "B Mecum" and "Bryce Mecum") refer to the same person is often referred to as record linkage or co-reference resolution. There is no universal solution that can be expected to work in all situations and it may be the case that many instances cannot be confidently linked. Two general approaches for record linkage might be used.
- Static matching (i.e. if name is the same, both records refer to the same thing)
- Machine learning (i.e. support vector machine on features such as Levenshtein distance)

I have experimented with both approaches and found value in both but I have also found limitations in both. Static matching is simple to understand and implement but it can be hard to add enough flexibility to handle common problems such as typographical errors or abbreviations in names. The machine learning approach is easy to implement but is a black box solution. However, this approach offers a great deal of flexibility. For the initial implementation of the tool that performs this task, only static matching will be used. The machine learning approach may be re-visited later on for use within this workflow or as a separate workflow which tries to establish linkages between existing HTTP URIs.

Proposed Approach:

1. Get a set of datasets (either from a dump or from the CN's Solr index)
2. Pre-process those datasets
3. Generate derived fields (i.e. full name = salutation + givenName + surName)
4. Run a static matcher over the datasets with a set of rules (i.e. if full name and email is the same, it's the same person)
5. Analyze final output for quality
6. Detect false positives

## Minting new HTTP URIs

### Minting Principles:

- It's okay if the same person has multiple HTTP URIs. We can later assert their sameness with something like `owl:sameAs`.
- Never assert two instances of a person or organization are the same person or organization (no false positives)
- URIs exist forever (URIs are never recycled or deleted)
- What those HTTP URIs resolve to may change
  - This is especially import because the DataOne API may change but we don't want these URIs to ever change and we will want them to resolve to the active/latest API.

Proposed Approach:

While it may seem reasonable to take a person in metadata record with the full name 'Bryce Mecum' and mint a nice HTTP URI like `https://www.dataone.org/people/brycemecum`, it is not feasible to do this for every person or organization given how many possible name collisions are possible, the vast number of non-ASCII characters present in names (i.e. 象形字), and the presence of datasets where only a last named was filled in. Universally Unique Identifiers (UUIDs) are a potential option.
- People URIs at `https://dataone.org/person/`
  - i.e. `https://dataone.org/person/urn:uuid:123e4567-e89b-12d3-a456-426655440000`

- Organization URIs at `https://dataone.org/organization/`
  - i.e. `https://dataone.org/organization/urn:uuid:123e4567-e89b-12d3-a456-426655440000`

UUIDs would be generated as UUID 4 (random) and checked for collision with existing UUIDs prior to establishing new HTTP URIs. Note that the above URIs use the `urn:uunid` prefix before the UUID itself. This is a workaround for the case when a UUID begins with a number.

DataOne manages a number of authentication services (See below: [Matching DataOne Accounts](#matching-dataone-accounts)). It is possible that, in the future, users from these services will have their own, human-readable HTTP URIs (like [http://dataone.org/people/brycemecum](http://dataone.org/people/brycemecum)). These URIs would be vastly preferable to a UUID4-based URI and should be used instead. This decision would be made prior to minting a new HTTP URI for an instance of a person in a dataset and would require some form of resolution between the authentication service and the graph generation service.

For some instances of people in datasets, it may be possible to make a highly confident match between the instance of that person and a person in an authentication system. For example, if the first name, last name, and email are the same in both systems, it is very likely that both instances refer to the same person. For instances of people in datasets without such identifying information, a match with a lower degree of certainty could be made which might still be useful to the person.

Summary:
- For most people and organizations, mint and maintain a UUID4-based URI.
- If we can match with 100% certainty to a DataOne account (i.e. both have an ORCID), re-use their user account portal URI (e.g. /people/brycemecum).
- If we cannot match them with 100% confidence but have more than 0% confidence, assert a property named something like `:couldBeSameAs`.


## Matching DataOne Accounts

Performing this record linkage activity for GeoLink project could be considered useful in and of itself. However, we have the opportunity to make this even more useful by integrating it with work already being done at DataOne on linking authenticated user accounts together. Users who directly interact with the DataOne network may have records in one or more authentication systems (e.g. LDAP) operated by DataOne. Any particular person, by having interacted with DataOne in multiple ways over time, may exist in multiple authentication systems and, therefore, have multiple accounts associated with themselves. DataOne is working on a manual tool for users to bundle their multiple accounts together under a single account. This record linkage activity within DataOne is useful because DataOne wants to be able to link scholarly work to people and having multiple accounts per person could splinter their scholarly work across multiple accounts. As for a person's datasets, they are often associated with a single account by virtue of the way metadata/data are uploaded and won't be immediately linked to that user's accounts in other authentication systems. This could change in the future if tools for uploading data to DataOne change but it remains a problem for now. Without the link between authentication systems, a person may not be able to find all of the datasets they have uploaded over time which would lessen the utility of what DataOne is offering.

The previous activity only solves the problem of linking users to their datasets for users that directly interact with the DataOne authentication systems. This is a very small subset of all the people and organizations who exist within metadata records. The work being done in the GeoLink project nicely fills this gap because we are already harvesting instances of people and organizations from the metadata in the DataOne network.

Instances of people and organizations we find within metadata records can be matched to people and organizations within the DataOne datasets and the datasets can then be linked to user accounts. However, the information about people and organizations that is present in metadata is often vague and may not provide enough information to conclusively match two instances of a person or organization together and/or match them to an DataOne account. Most metadata does not contain established, globally unique identifiers (such as ORCIDs) so the matching must be done on information such as name, organization, email, etc. Because this type of linkage is only a guess, it cannot be asserted that we are 100% sure the DataOne user with a name (e.g. Bryce Mecum) is the same person as the person who uploaded a dataset and filled in just their full name (e.g. Bryce Mecum).

In these cases where the match is not certain, we will use a different semantic concept (e.g. `mayBeTheSameAs`) than when we have 100% certain (as with ORCIDs) which could be done using `owl:sameAs`.

See [Service Integration](#service-integration) for a description of how the linkage between DataOne accounts and instances of people and organizations could be done.

## Graph Service

The graph service needs to run continuously and know about two things. The first is what datasets are new or updated since the last graph was created. This can be done with a Solr query like:

```{text}
https://cn.dataone.org/cn/v1/query/solr/?q=dateUploaded:[2015-05-30T23:21:15.567Z%20TO%202015-08-21T00:00:00.0Z]
```

In the above query, the first datetime is the last datetime the graph was updated, which the service needs to store, and the second datetime is the current time.

The second thing the service needs to know about is the existing set of people and organization HTTP URIs.

And with this information, the service needs to do the following things:
1. Attempt to find identical matches to people with human-readable HTTP URIs
2. Mint new HTTP URIs as necessary
  - Create the URI itself
  - Register that URI with some other service responsible for storing and resolving it

3. Update the latest DataOne RDF graph
  - Create new people and organization nodes for new people and organizations
  - Update information about existing people and organizations

4. Integrate knowledge of people and organizations with existing systems (Service Integration)
  - LDAP
  - CI Logon
  - DataOne Auth.

Updating existing people and organizations will involve updating both `glview:People` and `glview:Organization` resources as well as `glview:Dataset` resources.

Existing services on DataOne are Java programs but the language of the current implementation is Python. This can be changed.


### Graph Service Details

Because the graph of datasets needs to be kept up-to-date, triples will need to be added and/or removed over time in order to keep the RDF graph in sync with datasets in the network.
There is a chance here to integrate with existing infrastructure in DataOne and this may be the best way to do things.
In the existing system, when a dataset is added to a member node, a series of actions may be spun off, such as generating system metadata and replicating scientific metadata and the data itself to other nodes.
It's easy to imagine kicking off another action to direct another piece of DataOne infrastructure to analyze the newly-added dataset for information relevant to the RDF graph of datasets.

The alternative to this integrated service is to develop separate infrastructure which polls a coordinating node at regular intervals and initiates the necessary steps to update the RDF graph of datasets.

Assume we have a single triple-store which contains all the triples for all datasets.
Assume we have some URI database which stores already-minted URIs which can look up URIs by unique keys.
What should happen when datasets change?
Below I sketch out a number of scenarios and write out what should be done for each one:

#### New Dataset, New People, new Organizations

- Parse dataset, harvesting information on all concepts
- Check whether the dataset already exists in the triple store
  - Find it does not
- Check with the URI database for People/Oorganization URIs
  - Find there are all new People/Organizations
    - Mint new People/Organization URIs
- Generate triples and store them in the triple store

#### New Dataset, Some New & Existing People, Some New & Existing Organizations

- Parse dataset, harvesting information on all concepts
- Check whether the dataset already exists in the triple store
  - Find it does not exist
- Check with the URI database for People/Oorganization URIs
  - Find there are some existing, some new URIs
    - Fetch existing URIs for existing People and Organizations
    - Mint new People/Organization URIs for the new People and Organizations
- Generate triples and store them in the triple store
  - For each Person/Organization we already knew about, check whether their associated attributes (email, organization) that have been harvested from the current dataset are known.
    - For attributes that are already known, do nothing.
    - For attributes that are not known, added them to the triple store

#### Existing Dataset, Existing People, Existing Organizations
- Parse dataset, harvesting information on all concepts
- Check whether the dataset already exists in the triple store
  - Find it does exist
  - Remove all triples related to the dataset
- Check with the URI database for People/Oorganization URIs
  - Find all People/Organizations already have URIs
    - Fetch existing URIs for existing People and Organizations
- Generate triples and store them in the triple store
- For each Person/Organization, check whether their associated attributes (email, organization) that have been harvested from the current dataset are known.
  - For attributes that are already known, do nothing.
  - For attributes that are not known, added them to the triple store


There are a number of steps that are always executed, and some that are executed conditionally.

Always:
- Parse dataset, harvesting information on all concepts
- Check whether the dataset already exists in the triple store
- Check with the URI database for People/Oorganization URIs
- Generate triples and store them in the triple store
- For each Person/Organization, check whether their associated attributes (email, organization) that have been harvested from the current dataset are known.
  - For attributes that are already known, do nothing.
  - For attributes that are not known, added them to the triple store


### Issues

What to do about people URIs where we only have the name?

When a dataset is re-processed, we remove all the triples we added the last time the dataset was processed and then add them again with the (possibly) updated information.
When we re-process a dataset, either because it is updated or because we manually reprocess the dataset, people without sufficient distinguishing information (i.e., without emails addresses) will always trigger the minting of a new URI even though we minted them a new URI the last time their document was processed.
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


### DataOne Integration

Regarding #4 (above), when new HTTP URIs are created for a person or organization, that person or organization may exist in another system we operate. Ideally, at the time of creating a new HTTP URI also, we would find out of the person or organization we're creating a new HTTP URI for exists in other systems and make the appropriate associations. The key benefit of doing this would not just be directly linking, for example, someone in LDAP with their GeoLink HTTP URI but, instead, linking a someone in LDAP with datasets they created. In creating these linkages, it's important that no linkages that would result in changes to access privileges are made unless those changes are done through a secure system. For example, you wouldn't want to parse an EML document, find a person in LDAP with similar name, and allow that person to delete that dataset. It would be good to present linkages we have confidence in to the authenticated user (e.g. on LDAP) and allow them to confirm or deny sameness.

Once the linkages are made, visiting a person's user account page (e.g. [http://dataone.org/people/brycemecum](http://dataone.org/people/brycemecum)) would show both datasets that certainly reference the user as well as datasets that may reference the user. These linkages could be confirmed or denied by the logging-in user. Linkages made in this way would still be imperfect because a user could mistakenly claim someone else's data when the data weren't uploaded with sufficiently unique identifying information. But if, for example, the dataset contained a DataOne URI or an ORCID and the user account had one of these identifiers, then the match between the user and the reference to a person in the dataset would be essentially certain (absent typos).

In the above scenario, a user account might contain hierarchical person information such as:
- [http://dataone.org/people/brycemecum](http://dataone.org/people/brycemecum) [an authenticated account]
  - matches: [http://dataone.org/people/123e4567-e89b-12d3-a456-426655440000](http://dataone.org/people/123e4567-e89b-12d3-a456-426655440000) [a possible match]
  - hasAccount: CN=Bryce Mecum A81283,O=Google,C=US,DC=cilogon,DC=org [an authenticated match]
  - hasConfirmedMatch: [https://dataone.org/person/123e4567-e89b-12d3-a456-426655440549](https://dataone.org/person/123e4567-e89b-12d3-a456-426655440549) [user indicated this is them]

And from this hierarchical set of user information, we could link in datasets attributed to these people.


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
