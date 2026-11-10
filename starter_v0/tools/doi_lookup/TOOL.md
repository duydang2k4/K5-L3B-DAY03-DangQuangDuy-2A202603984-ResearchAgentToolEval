---
name: doi_lookup
track: bonus
kind: live_api
provider: Crossref REST API
requires_env: []
inputs: [doi]
outputs: [doi, title, authors, year, journal, url, citation_count, source]
side_effect: false
---
# doi_lookup

Looks up bibliographic metadata for an exact DOI using Crossref's public REST API.
Accepts a bare DOI or a doi.org URL. It does not search by topic or read full text.
Invalid input and HTTP errors return an error dict.
