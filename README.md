# econbiz-mcp

An [MCP](https://modelcontextprotocol.io) server for the [EconBiz API v1](https://api.econbiz.de/). It lets an AI assistant search economics and business literature, fetch full records, find similar works, check access options and autocomplete terms. No API key is needed.

## Table of contents

- [About EconBiz](#about-econbiz)
- [Tools](#tools)
- [Installation](#installation)
- [Configuration](#configuration)
- [Skill](#skill)
- [Versions and updates](#versions-and-updates)
- [Example prompts](#example-prompts)
- [Development](#development)
- [Testing status](#testing-status)
- [Limitations](#limitations)
- [Disclaimer and license](#disclaimer-and-license)

## About EconBiz

[EconBiz](https://www.econbiz.de/) is the literature search portal of the [ZBW – Leibniz Information Centre for Economics](https://www.zbw.eu/), the German National Library of Economics. It covers economics and business studies: books, journal articles, working papers, conference papers and grey literature.

Why it is worth connecting to an assistant, measured against the live API in October 2026:

- **Size:** about 10.4 million records, mostly from ECONIS (the ZBW library catalogue, 6.7M), RePEc (1.9M) and EconStor (0.3M, the ZBW open-access repository).
- **German-language literature:** about 1.4 million records are tagged as German, including around 500,000 articles. That is a lower bound, because the language field is not always filled. German journals and monographs are often missing from international databases, which is the main reason to use EconBiz alongside them.
- **Structure:** bilingual subject terms (STW Thesaurus), JEL codes, journal-level search and links to free full texts where they exist.

I found no independent comparison with other databases, so this README does not claim that EconBiz has the best coverage, only that it is a strong source for German-language economics literature.

## Tools

| Tool | API endpoint | Purpose |
|---|---|---|
| `search` | `/v1/search` | Search with Lucene query syntax, paging, facets, facet filters, sorting, spellcheck |
| `get_record` | `/v1/record/{id}` | Full metadata of one record, optionally with "more like this" snippets |
| `get_availability` | `/v1/record/{id}/avail/{client}` | Full text links, DOI, subito order, holdings |
| `find_similar` | `/v1/search/{id}?mlt=` | Records similar to a given one, by author or subject |
| `suggest` | `/v1/suggest/` | Autocomplete terms with counts |
| `list_fields` | `/v1/fields` | Fields and their scopes (display, facet, search, sort, suggest) |

### `search` parameters

| Parameter | Description |
|---|---|
| `query` | Lucene syntax. `AND` is the default operator. Supports `AND`/`OR`/`NOT`, `"phrases"`, fielded search (`title:"knowledge management"`), `(grouping)`, wildcards (`title:Leasing*`) and year ranges (`date:[2020 TO 2026]`). Special characters must be Lucene-escaped. |
| `size` / `start` | Page size (API default 10) and 1-based position of the first hit |
| `fulltext` | Additionally search full texts (only partly available); widens the result set, does not restrict it |
| `facets` | Fields to count, e.g. `["date", "person", "subject"]` |
| `facet_size` | Max items per facet (API default 40) |
| `filters` | Facet filters as `field:value`, e.g. `["date:2007", "person:\"Nonaka, Ikujiro\""]` |
| `sort` | e.g. `date desc`; default is relevance (`score desc`) |
| `spellcheck` | Return a corrected query with its hit count |
| `echo` | Echo the parsed query and facet values |

**Mapping to the raw API:** some parameters are renamed to be clearer for an LLM.

| Tool parameter | API parameter |
|---|---|
| `query` | `q` |
| `start` | `from` |
| `filters` | `facet` (the alias `ff` is not exposed) |
| `more_like_this` / `similarity` | `mlt` |
| `prefix` (suggest) | `q` |

Booleans are sent as `on`/`off`, and list values as repeated parameters. Not exposed: `pretty` (only affects formatting), `profile` (set via `ECONBIZ_PROFILE`) and `oid` of `suggest` (undocumented by the API).

Use `list_fields` with `scope` set to `search`, `facet`, `sort` or `suggest` to see which fields work in each place.

### Other tools

- `get_record(record_id, more_like_this=["author", "subject"])`
- `get_availability(record_id, client=None)`: `client` is an IP address or library ID.
- `find_similar(record_id, similarity, size, start, facets, filters, sort)`: exactly one of `author` or `subject`.
- `suggest(prefix, field="text", opensearch=False)`: `field` is one of `text`, `person`, `subject`, `title`, `institution`, `publisher`, `isPartOf`, `isn`.

API errors are returned with the API's own message, for example `EconBiz API error 400: Illegal record id: 1`.

## Installation

Requires [uv](https://docs.astral.sh/uv/). There is nothing to clone: clients run the server straight from GitHub with `uvx`. Check that it starts:

```bash
uvx --from git+https://github.com/mbravidor/econbiz-mcp econbiz-mcp
```

This prints nothing and waits for MCP messages on stdin, which means it started correctly. Stop it with Ctrl+C.

Then add it to your client. Ready-to-use files are in [`configs/`](configs); open your client below. Merge the `econbiz` entry into an existing config file instead of overwriting it.

### Claude Code

```bash
claude mcp add econbiz --scope user -- uvx --from git+https://github.com/mbravidor/econbiz-mcp econbiz-mcp
```

`--scope user` makes it available in all projects. Add `-e ECONBIZ_APP_NAME=yourname` before the `--` to set the app name. Alternatively, put the JSON below in `.mcp.json` in your project root.

<details>
<summary>.mcp.json</summary>

```json
{
  "mcpServers": {
    "econbiz": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "git+https://github.com/mbravidor/econbiz-mcp", "econbiz-mcp"],
      "env": {
        "ECONBIZ_APP_NAME": "econbizmcp"
      }
    }
  }
}
```

</details>

### Other clients

<details>
<summary><b>Claude Desktop</b></summary>

Settings → Developer → *Edit Config*. File: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows).

```json
{
  "mcpServers": {
    "econbiz": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/mbravidor/econbiz-mcp", "econbiz-mcp"],
      "env": {
        "ECONBIZ_APP_NAME": "econbizmcp"
      }
    }
  }
}
```

</details>

<details>
<summary><b>opencode</b></summary>

File: `opencode.json` in your project or `~/.config/opencode/opencode.json`. opencode uses `mcp`, with the command as one array.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "econbiz": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/mbravidor/econbiz-mcp", "econbiz-mcp"],
      "enabled": true,
      "environment": {
        "ECONBIZ_APP_NAME": "econbizmcp"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Zoo Code / Roo Code</b></summary>

MCP icon → *Edit Global MCP* (`mcp_settings.json`) or *Edit Project MCP* (`.roo/mcp.json`). `alwaysAllow` skips the approval prompt; all tools are read-only. Remove it to confirm each call. [`roo-code.json`](configs/roo-code.json) is identical to [`zoo-code.json`](configs/zoo-code.json).

```json
{
  "mcpServers": {
    "econbiz": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/mbravidor/econbiz-mcp", "econbiz-mcp"],
      "env": {
        "ECONBIZ_APP_NAME": "econbizmcp"
      },
      "alwaysAllow": ["search", "get_record", "get_availability", "find_similar", "suggest", "list_fields"],
      "disabled": false
    }
  }
}
```

</details>

<details>
<summary><b>Cline</b></summary>

MCP Servers → *Configure* → *Configure MCP Servers* (`cline_mcp_settings.json`). The Cline CLI uses `~/.cline/data/settings/cline_mcp_settings.json`. Cline calls the approval list `autoApprove`.

```json
{
  "mcpServers": {
    "econbiz": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/mbravidor/econbiz-mcp", "econbiz-mcp"],
      "env": {
        "ECONBIZ_APP_NAME": "econbizmcp"
      },
      "disabled": false,
      "autoApprove": ["search", "get_record", "get_availability", "find_similar", "suggest", "list_fields"]
    }
  }
}
```

</details>

<details>
<summary><b>Cursor</b></summary>

File: `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global).

```json
{
  "mcpServers": {
    "econbiz": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "git+https://github.com/mbravidor/econbiz-mcp", "econbiz-mcp"],
      "env": {
        "ECONBIZ_APP_NAME": "econbizmcp"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Windsurf</b></summary>

*Open MCP config file* in the Cascade panel. Current docs name `~/.config/devin/mcp_config.json`; older versions used `~/.codeium/windsurf/mcp_config.json` (not re-verified).

```json
{
  "mcpServers": {
    "econbiz": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/mbravidor/econbiz-mcp", "econbiz-mcp"],
      "env": {
        "ECONBIZ_APP_NAME": "econbizmcp"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Gemini CLI</b></summary>

Put the `mcpServers` key in `.gemini/settings.json` (project) or `~/.gemini/settings.json` (user). The folder must be trusted (`gemini trust`).

```json
{
  "mcpServers": {
    "econbiz": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/mbravidor/econbiz-mcp", "econbiz-mcp"],
      "env": {
        "ECONBIZ_APP_NAME": "econbizmcp"
      }
    }
  }
}
```

</details>

<details>
<summary><b>VS Code (Copilot)</b></summary>

File: `.vscode/mcp.json`, or *MCP: Open User Configuration*. VS Code uses `servers`, not `mcpServers`.

```json
{
  "servers": {
    "econbiz": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "git+https://github.com/mbravidor/econbiz-mcp", "econbiz-mcp"],
      "env": {
        "ECONBIZ_APP_NAME": "econbizmcp"
      }
    }
  }
}
```

</details>


GUI clients often do not inherit your shell `PATH`. If `uvx` is not found, put its absolute path (`which uvx`) in `command`.

## Configuration

| Variable | Description |
|---|---|
| `ECONBIZ_APP_NAME` | Short alphanumeric application name, sent as User-Agent. The API terms encourage developers to identify their app. Default `econbizmcp`. |
| `ECONBIZ_PROFILE` | Name of an EconBiz user profile (API `profile` parameter). Leave unset unless you have a registered profile: the API answers `400 Bad Request` to every call with an unknown profile name (tested with `default`, `econbiz`, `portal`). |

## Skill

[`skills/econbiz-research/SKILL.md`](skills/econbiz-research/SKILL.md) is an optional agent skill that teaches a model how to search EconBiz well: the query syntax and the recall pitfalls (German compound words, incomplete subject indexing, first-author-only `creator`, and so on). It expects the MCP tools above. Install it by copying the folder into your agent's skills directory:

```bash
cp -r skills/econbiz-research ~/.claude/skills/        # Claude Code (opencode also reads this directory)
cp -r skills/econbiz-research ~/.config/opencode/skills/   # opencode only
```

Other tools use other directories; check their docs. Re-copy after updating the repo.

## Versions and updates

Releases are git tags (`v0.1.0`, `v0.1.1`, `v0.2.0`, ...; see [`CHANGELOG.md`](CHANGELOG.md)).

- **Unpinned** (`...econbiz-mcp` as in the configs) follows `main`.
- **Pinned**: append the tag, e.g. `git+https://github.com/mbravidor/econbiz-mcp@v0.2.0`. For Claude Code:

  ```bash
  claude mcp remove econbiz -s user
  claude mcp add econbiz --scope user -- uvx --from git+https://github.com/mbravidor/econbiz-mcp@v0.2.0 econbiz-mcp
  ```
- **Updating**: `uvx` caches the checkout, so an unpinned install can keep serving old code. Run once with `--refresh` to pull the latest: `uvx --refresh --from git+https://github.com/mbravidor/econbiz-mcp econbiz-mcp` (stop it with Ctrl+C), then restart your client.

## Example prompts

- "Find recent articles on knowledge management, newest first, and show the top subjects."
- "Which papers by Ikujiro Nonaka are in EconBiz? Filter to 2007."
- "Is record 10015595151 available as free full text? Show similar records by subject."
- "Suggest subject terms starting with *behavioral econ*."

## Development

Agents and contributors: see [`AGENTS.md`](AGENTS.md) for gotchas and the doc/config sync rules.

```bash
uv sync
uv run python -c "import asyncio; from econbiz_mcp import server as s; print(asyncio.run(s.search('inflation', size=1)))"
```

The server is a single file, `src/econbiz_mcp/server.py`, built on the official MCP Python SDK (`FastMCP`, pinned to `mcp<2`) and `httpx`.

## Testing status

The server was tested against the live API through a real MCP stdio session, and the install from GitHub was verified with `uvx`. Of the client configs, only Claude Code was actually run (it reports *Connected*). The others follow each client's documentation but were not run in the clients themselves, so report any that need adjusting.

## Limitations

- The API is in beta. Only the documented methods and parameters are stable for v1.
- Response bodies are returned as the API sends them. Their structure is only partly documented.
- Full-text search covers only part of the corpus.
- Record IDs must be numeric; anything else is rejected before a request is made.
- A fielded query on a field that does not exist (e.g. `bogus:x`) silently returns 0 hits instead of an error. Check field names with `list_fields`.
- Facet filters accept single values only (`date:2007`); ranges like `date:[2000 TO 2010]` return HTTP 400 there. Range queries work inside `query` (`nonaka AND date:[2000 TO 2010]`).
- `fulltext` widens the search to full texts; it does not restrict results to records with full text.
- `creator` may list only the first author of a multi-author record; use `title_responsible` from `get_record` for the full statement.

## Disclaimer and license

This is an unofficial community project. It is not affiliated with or endorsed by the ZBW. Data comes from the EconBiz API and is subject to its [terms of use](https://api.econbiz.de/): the service is in beta, offers no guaranteed availability, and is not meant for copying EconBiz content at scale.

MIT License, see [`LICENSE`](LICENSE).
