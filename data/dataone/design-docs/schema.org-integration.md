# DataONE Google Search / JSON-LD Integration Design Notes

Problem: DataONE's dataset landing pages are not indexed by Google

Causes:

- MetacatUI's use of fragment URLs (e.g., #view/{PID}) (I'm not 100% sure on this but this seems like the culprit. It may also have something to do with our use of a client-side web app)
- Landing pages don't include Structured Data (e..g, JSON-LD describing a Schema.org/Dataset resource)

Benefits: Making DataONE indexable by Google make a positive impact to the DataONE community (both scientists/users and member node operators) and the scientific community at large.
DataONE Search currently allows users to search for datasets contained within DataONE but the user must know about DataONE Search. We can assume every use knows about Google and, therefore, this change should be expected to increase traffic to DataONE Search which is a positive impact.

Tasks:

1. Investigate the feasibility of no longer using Fragment URLs in MetacatUI

    Notes:

    - The solution will need to gracefully redirect users from the previous Fragment URLs to the new URL so bookmarks/links and, more importantly DOIs don't break. This is very important.

    - The change will need to be discussed with the NCEAS team (esp. Lauren Walker, Chris Jones) as well as the DataONE team.

2. Investigate what it would take for Google to index our dataset landing pages

3. Investigate what's needed to support Google's Structured Dataset initiative (putting JSON-LD on dataset landing pages)

    Notes:

    - This may interact with Task 2. Our landing pages may not need to be crawlable by Google Search if they provide Structured Data instead.

    - If Google prefers Structured Data over parsing the full page, we may find doing both is redundant. Compare both options.
