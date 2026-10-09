---
name: econbiz-research
description: Search EconBiz (api.econbiz.de), the ZBW literature portal for economics and business studies, through the econbiz MCP tools (search, get_record, get_availability, find_similar, suggest, list_fields). Use for literature searches in economics, business, accounting, finance, tax or management, especially when German-language journals, monographs, textbooks or working papers matter. Covers EconBiz query syntax and the recall pitfalls that hide relevant records.
---

# EconBiz literature search

Use the `econbiz` MCP tools. Do not scrape `www.econbiz.de` (bot-protected); link to records as `https://www.econbiz.de/Record/{id}`.

## Workflow

1. Translate the topic into German and English terms. Subjects are bilingual, titles are usually monolingual. Find controlled terms with `suggest(prefix, field="subject")`.
2. Run several tight queries with `search`, not one broad one. Use `facets=["date","language","type"]` to see how the hits distribute.
3. Verify every item you will cite with `get_record` and take bibliographic data from there, never from memory.
4. Report which queries you ran so coverage can be judged.

## Query syntax

- **`AND` is the default operator**, so `knowledge management` means both words. Write `OR` explicitly.
- Fields: `title:`, `creator:`, `subject:`, `isPartOf:` (journal), `jel:`, `type:`, `source:`, `isn:`. Check valid names with `list_fields(scope="search")`. An unknown field silently returns 0 hits.
- Phrases in quotes; grouping with parentheses; `NOT`; wildcards `*` and `?`.
- Year ranges work inside the query: `date:[2020 TO 2026]`. They do **not** work in `filters`, which take single values only (`date:2020`).
- Language codes are ISO 639-2/B: `language:deu`, `language:eng`. `language:ger` silently returns 0 hits.
- `fulltext=true` does not restrict to records with full text; it additionally searches full texts, so it widens the result set.

## Recall pitfalls

1. **German compounds are single tokens.** `title:Leasing` does not match *Leasingverhältnissen*. Use `title:Leasing*`, or combine, e.g. `title:Leasing* AND title:IFRS*`.
2. **Subject indexing is incomplete.** Some records have no subject terms. Use `subject:` for precision, not as a hard filter in recall-critical searches.
3. **Signal words vary.** Case studies may say *Fallstudie*, *Fallbeispiel*, *am Beispiel* or nothing. Do not require one. Series such as IRZ's "der Fall - die Lösung" carry only a suffix, so try `title:"der Fall"` for IRZ.
4. **Relevance ranking buries hits.** For thorough sweeps use tight fielded queries, page with `size=100` and `start` (if the output is too large for your client, use 30-40 per page), and finish with known-item probes (`creator:Name`, `title:"exact phrase"`).
5. **Few hits does not mean sparse coverage.** Retry with truncation, synonyms and the other language before concluding that.
6. **Zero hits does not mean a source does not exist.** New or practitioner-oriented books can be missing. Check the publisher before calling a source fabricated.
7. **Journal searches:** `isPartOf:"<indexed title>"` works. `isn:` (ISSN) is only partly populated, so do not rely on it. Journals are indexed under varying strings; use `suggest(field="isPartOf")` to find the exact one.

## Authors and duplicates

- `creator` can list only the first author. For the full list use `title_responsible` from `get_record`, and cross-check `person` and `contributor`. Do not build citation metadata from `creator` alone.
- **Before citing, run `get_record`** on every item whose list-view data lacks volume, issue or pages. The search hit shows a shortened `isPartOf` and omits `language`; `get_record` has the full journal statement, `language` and `title_responsible`. The `language` field can disagree with the title (a German-titled KoR article is indexed as `eng`), so check it when language matters.
- Names in case-study titles can be company names, not authors.
- The index contains duplicates (often title-casing variants). Deduplicate by DOI when present (`identifier_number`, formatted `10.x/y [DOI]`), otherwise by normalized title and year. Print and e-book records of the same book are separate records (the e-book carries the DOI), so match books by title, author and year. Two records can share a DOI yet list different first authors (one may be an EconStor record that carries the free PDF; prefer that one for open access), so do not dedupe by creator.
- Citation counts (`citations`) are sparsely populated. Do not treat them as reliable.

## Limits

No quota, but bulk copying is against the terms of use. Keep `size` at 100 or below per page and do not crawl.
