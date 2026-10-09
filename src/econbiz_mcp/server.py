"""MCP server exposing the EconBiz API v1 (https://api.econbiz.de/)."""

import os
from typing import Any, Literal
from urllib.parse import quote

import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = "https://api.econbiz.de/v1"
# Optional: a short alphanumeric application name, as requested by the API terms of use.
APP_NAME = os.environ.get("ECONBIZ_APP_NAME", "econbizmcp")
PROFILE = os.environ.get("ECONBIZ_PROFILE")

mcp = FastMCP("econbiz")

Similarity = Literal["author", "subject"]


_client: httpx.AsyncClient | None = None


def _http() -> httpx.AsyncClient:
    """Shared client, so chained tool calls reuse the TLS connection."""
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=30, follow_redirects=True, headers={"User-Agent": f"{APP_NAME} (econbiz-mcp)"}
        )
    return _client


def _record_path(record_id: str) -> str:
    """EconBiz record IDs are numeric; reject anything else (e.g. '..') before building a URL."""
    record_id = record_id.strip()
    if not record_id.isdigit():
        raise ValueError(f"Invalid EconBiz record id {record_id!r}: expected digits only, e.g. 10015595151")
    return f"record/{record_id}"


async def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    """GET an API path; list values become repeated params, booleans on/off."""
    query: list[tuple[str, str]] = []
    for key, value in (params or {}).items():
        values = value if isinstance(value, list) else [value]
        for v in values:
            if v is None or v == "":
                continue
            query.append((key, ("on" if v else "off") if isinstance(v, bool) else str(v)))
    if PROFILE:
        query.append(("profile", PROFILE))
    try:
        resp = await _http().get(f"{BASE_URL}/{path}", params=query)
    except httpx.HTTPError as e:
        raise RuntimeError(f"EconBiz request failed ({type(e).__name__}): {e}") from e
    try:
        data = resp.json()
    except ValueError:
        data = None
    if resp.status_code >= 400 or not 200 <= resp.status_code < 300:
        msg = data.get("message") if isinstance(data, dict) else None
        hint = " (check ECONBIZ_PROFILE: unknown profiles are rejected)" if PROFILE and resp.status_code == 400 else ""
        raise RuntimeError(f"EconBiz API error {resp.status_code}: {msg or resp.text[:200]}{hint}")
    if data is None:
        raise RuntimeError(f"EconBiz API returned non-JSON content (HTTP {resp.status_code}): {resp.text[:200]}")
    return data


@mcp.tool()
async def list_fields(scope: Literal["display", "facet", "search", "sort", "suggest"] | None = None) -> Any:
    """List EconBiz fields and which capabilities each has.

    scope: restrict to fields usable for 'display', 'facet' (facets/filters), 'search'
    (fielded search, e.g. title:knowledge), 'sort' or 'suggest'. Omit to get all fields
    with their per-scope flags.
    """
    return await _get("fields", {"scope": scope})


@mcp.tool()
async def search(
    query: str,
    size: int = 10,
    start: int = 1,
    fulltext: bool = False,
    facets: list[str] | None = None,
    facet_size: int | None = None,
    filters: list[str] | None = None,
    sort: str | None = None,
    spellcheck: bool = False,
    echo: bool = False,
) -> Any:
    """Search the EconBiz literature index (economics and business studies).

    query: Lucene syntax; AND is the default operator. Supports AND/OR/NOT, "phrases",
      fielded search (title:"knowledge management", creator:nonaka), (grouping),
      wildcards (title:Leasing*) and year ranges (date:[2020 TO 2026]).
      Special characters must be Lucene-escaped. Tips: German compounds are single
      tokens, so use wildcards (Leasing* finds Leasingverhältnisse); language codes are
      ISO 639-2/B (language:deu, not ger); unknown fields silently return 0 hits;
      subject indexing is incomplete, so don't use subject: as a hard filter.
    size: max records returned (API default 10).
    start: 1-based position of the first record (for paging).
    fulltext: additionally search full texts (only partly available). This widens the
      result set; it does not restrict to records that have full text.
    facets: fields to compute facet counts for, e.g. ["date", "person", "subject"]
      (see list_fields with scope=facet).
    facet_size: max items per facet (API default 40).
    filters: facet value filters as 'field:value', e.g. ['date:2007', 'person:"Nonaka, Ikujiro"'].
      Single values only; for year ranges put date:[2020 TO 2026] in the query instead.
      Quote values containing blanks, commas or special characters.
    sort: e.g. 'date desc' (default is relevance 'score desc'); see list_fields scope=sort.
    spellcheck: return a corrected-query suggestion with hit count.
    echo: echo the parsed query and facet values in the response.

    Returns a list-view subset of metadata per hit; use get_record for full details.
    Note: 'creator' may list only the first author; get_record's 'title_responsible'
    has the full author statement.
    """
    return await _get("search", {
        "q": query, "size": size, "from": start, "fulltext": fulltext if fulltext else None,
        "facets": facets, "facet_size": facet_size, "facet": filters, "sort": sort,
        "spellcheck": spellcheck if spellcheck else None, "echo": echo if echo else None,
    })


@mcp.tool()
async def get_record(record_id: str, more_like_this: list[Similarity] | None = None) -> Any:
    """Get full metadata for one EconBiz record by its ID.

    more_like_this: also include snippets of similar records, by 'author' (personal and
    corporate creators) and/or 'subject' (keywords and classifications).
    """
    return await _get(_record_path(record_id), {"mlt": more_like_this})


@mcp.tool()
async def get_availability(record_id: str, client: str | None = None) -> Any:
    """Get access/availability options (full text links, DOI, subito order, library holdings)
    for a record.

    client: optional client identifier such as an IP address or library ID; if given,
    availability is tailored to that client.
    """
    path = f"{_record_path(record_id)}/avail"
    if client:
        if client.strip(".") == "":
            raise ValueError(f"Invalid client identifier {client!r}")
        path += f"/{quote(client, safe='')}"
    return await _get(path)


@mcp.tool()
async def find_similar(
    record_id: str,
    similarity: Similarity,
    size: int = 10,
    start: int = 1,
    facets: list[str] | None = None,
    filters: list[str] | None = None,
    sort: str | None = None,
) -> Any:
    """Run a 'more like this' search: records similar to the given record.

    similarity: exactly one measure - 'author' (shared creators) or 'subject' (shared
    keywords/classifications). Supports the same paging, facets, filters and sort as search.
    """
    return await _get(f"search/{_record_path(record_id).split('/')[1]}", {
        "mlt": similarity, "size": size, "from": start,
        "facets": facets, "facet": filters, "sort": sort,
    })


@mcp.tool()
async def suggest(
    prefix: str,
    field: Literal["text", "institution", "isPartOf", "isn", "person", "publisher", "subject", "title"] = "text",
    opensearch: bool = False,
) -> Any:
    """Autocomplete a partial input (term completions with counts).

    field: suggest source - 'text' (default, general), 'person', 'subject', 'title',
      'institution', 'publisher', 'isPartOf' (journal/series) or 'isn' (ISSN/ISBN).
    opensearch: return the OpenSearch suggestion format instead of terms with counts.
    """
    return await _get("suggest/", {"field": field, "q": prefix, "opensearch": opensearch if opensearch else None})


def main() -> None:
    try:
        mcp.run()
    except KeyboardInterrupt:
        pass  # Ctrl+C in a terminal is a normal way to stop a stdio server


if __name__ == "__main__":
    main()
