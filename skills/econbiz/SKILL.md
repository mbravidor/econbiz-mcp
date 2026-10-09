---
name: econbiz
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
3. **Signal words vary.** Case studies may say *Fallstudie*, *Fallbeispiel*, *am Beispiel* or nothing. Do not require one.
4. **Relevance ranking buries hits.** For thorough sweeps use tight fielded queries, page with `size=100` and `start`, and finish with known-item probes (`creator:Name`, `title:"exact phrase"`).
5. **Few hits does not mean sparse coverage.** Retry with truncation, synonyms and the other language before concluding that.
6. **Zero hits does not mean a source does not exist.** New or practitioner-oriented books can be missing. Check the publisher before calling a source fabricated.
7. **Journal searches:** `isPartOf:"<indexed title>"` works. `isn:` (ISSN) is only partly populated, so do not rely on it. Journals are indexed under varying strings; use `suggest(field="isPartOf")` to find the exact one.

## Authors and duplicates

- `creator` can list only the first author. For the full list use `title_responsible` from `get_record`, and cross-check `person` and `contributor`. Do not build citation metadata from `creator` alone.
- Names in case-study titles can be company names, not authors.
- The index contains duplicates (often title-casing variants). Deduplicate by DOI when present (`identifier_number`, formatted `10.x/y [DOI]`), otherwise by normalized title and year.
- Citation counts (`citations`) are sparsely populated. Do not treat them as reliable.

## Limits

No quota, but bulk copying is against the terms of use. Keep `size` at 100 or below per page and do not crawl.
