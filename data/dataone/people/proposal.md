---
author: Bryce Mecum
email: mecum@nceas.ucsb.edu
---

# Proposal for Handling DataOne People & Organizations

## Contents

- [Overview](#overview)
- [Finding unique people and organizations](#finding-unique-people-and-organizations)
- [Minting new HTTP URIs](#minting-new-http-uris)
- [The Service](#the-service)
- [Timeline](#timeline)
- [Notes](#notes)


## Overview

The linked open data (LOD) graph for the datasets that exist in DataOne's network is nearly complete.
However, resources of type `glview:People` and `glview:Organization` are not represented as HTTP URIs but they need to be in order for our RDF graph to be an LOD RDF graph.
Instances of these two concepts present in DataOne datasets often are represented by the person or organization's name but do not come with existing LOD HTTP URIs we can re-use in our graph.
Therefore, new HTTP URIs will need to be created for instances of people and organizations that across datasets in the DataOne network.

Complicating this task, many instances of a person or organization present in the metadata may actually refer to the same person or organization.
When this is the case, we don't want to mint separate HTTP URIs for each instance of the same person or organization and instead we want to re-use existing HTTP URIs when appropriate.

The task of giving existing people and organizations HTTP URIs can be broken up into two parts:

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
For the initial implementation of the tool that performs this task, only static matching will be used.
The machine learning approach may be re-visited later on for use within this workflow or as a separate workflow which tries to establish linkages between existing HTTP URIs.


### Proposed Approach

1. Get a set of datasets (either from a dump or from the CN's Solr index)
2. Pre-process those datasets
  - Generate derived fields (i.e. full name = salutation + givenName + surName)
3. Run a static matcher over the datasets with a set of rules (i.e. if full name and email is the same, it's the same person)
4. Analyze final output for quality
  - Detect false positives

## Minting new HTTP URIs

### URI Principles:

- It's okay if the same person has multiple HTTP URIs. We can later assert their sameness.
- Never assert two instances of a person or organization are the same person or organization (no false positives)
- URIs exist forever (URIs are never recycled or deleted)
- What those HTTP URIs resolve to may change
  - This is especially import because the DataOne API may change but we don't want these URIs to ever change and we will want them to resolve to the active/latest API.


### Proposed Approach

While it may seem reasonable to have nice HTTP URIs like `https://www.dataone.org/people/brycemecum`, it does not seem feasible given how many possible name collisions are possible, the vast number of non-ASCII characters present in names (i.e. 象形字), and the presence of datasets where only a last named was filled in.
Universally Unique Identifiers (UUIDs) are a potential option.

- People URIs at `https://dataone.org/person/`
  - i.e. `https://dataone.org/person/123e4567-e89b-12d3-a456-426655440000`
- Organization URIs at `https://dataone.org/organization/`
  - i.e. `https://dataone.org/organization/123e4567-e89b-12d3-a456-426655440000`


If a UUID-based scheme were chosen, UUIDs would be generated as UUID 4 (random) and checked for collision with existing UUIDs prior to establishing new HTTP URIs.

Aside: DataOne already has some people HTTP URIs, e.g. https://www.dataone.org/dataone_leadership_team/matthew-jones but I don't think this format (org/person) needs to be used here.

DataOne manages a number of authentication services (See below: Service Integration).
It is possible that, in the future, users from these services will have their own, human-readable HTTP URIs (like http://dataone.org/people/brycemecum).
These URIs would be vastly preferable to a UUID4-based URI and should be used instead.
This decision would be made prior to minting a new HTTP URI for an instance of a person in a dataset and would require some form of resolution between the authentication service and the graph generation service.

For some instances of people in datasets, it may be possible to make a highly probably match between the instance of that person and a person in an authentication system.
For example, if the first name, last name, and email are the same in both systems, it is highly probably that both things refer to the same person.
For instances of people in datasets without such identifying information, a match with a lower degree of certainty could be made which might still be useful to the person.


## The Service

The service needs to run continuously and know about two things. The first is what datasets are new or updated since the last graph was created.
This can be done with a Solr query like:

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
  - C1 Logon
  - DataOne Auth.

Updating existing people and organizations will involve updating both `glview:People` and `glview:Organization` resources as well as `glview:Dataset` resources.

Existing services on DataOne are Java programs but the language of the current implementation is Python. This can be changed.

### Service Integration

Regarding #4 (above), when new HTTP URIs are created for a person or organization, that person or organization may exist in another system we operate.
Ideally, at the time of creating a new HTTP URI also, we would find out of the person or organization we're creating a new HTTP URI for exists in other systems and make the appropriate associations.
The key benefit of doing this would not just be directly linking, for example, someone in LDAP with their GeoLink HTTP URI but, instead, linking a someone in LDAP with datasets they created.
In creating these linkages, it's important that no linkages that would result in changes to access privileges are made unless those changes are done through a secure system. For example, you wouldn't want to parse an EML document, find a person in LDAP with similar name, and allow that person to delete that dataset.
It would be good to present linkages we have confidence in to the authenticated user (e.g. on LDAP) and allow them to confirm or deny sameness.

Once the linkages are made, visiting a person's user account page (e.g. http://dataone.org/people/brycemecum) would show both datasets that certainly reference the user as well as datasets that may reference the user.
These linkages could be confirmed or denied by the logging-in user.
Linkages made in this way would still be imperfect because a user could mistakenly claim someone else's data when the data weren't uploaded with sufficiently unique identifying information.
But if, for example, the dataset contained a DataOne URI or an ORCID and the user account had one of these identifiers, then the match between the user and the reference to a person in the dataset would be essentially certain (absent typos).

In the above scenario, a user account might contain hierarchical person information such as:

- http://dataone.org/people/brycemecum [an authenticated account]
  - matches: http://dataone.org/people/123e4567-e89b-12d3-a456-426655440000 [a possible match]
  - hasAccount: CN=Bryce Mecum A81283,O=Google,C=US,DC=cilogon,DC=org [an authenticated match]
  - hasConfirmedMatch: https://dataone.org/person/123e4567-e89b-12d3-a456-426655440549 [user indicated this is them]

And from this hierarchical set of user information, we could link in datasets attributed to these people.

## Timeline

Creating the pieces outlined above will take a great deal of work as a whole but can be broken down into sequential deliverables with an attached timeline.

- Create initial LOD graph of existing DataOne datasets: September 4
- Create service which pulls new metadata and integrates it into the graph: September 18
- Integrate with DataOne V2 API: TBD


## Notes
Use of solr dateModified

dateSysMetadataModified (Solr: dateModified)
Type: Types.xs.dateTime

Date and time (UTC) that this system metadata record was last modified in the DataONE system. This is the same timestamp as dateUploaded until the system metadata is further modified. The Member Node must set this optional field when it receives the system metadata document from a client.


dateUploaded (Solr: dateUploaded)
Type: Types.xs.dateTime

Date and time (UTC) that the object was uploaded into the DataONE system, which is typically the time that the object is first created on a Member Node using the MNStorage.create() operation. Note this is independent of the publication or release date of the object. The Member Node must set this optional field when it receives the system metadata document from a client.
