# econbiz-mcp

An [MCP](https://modelcontextprotocol.io) server for the [EconBiz API v1](https://api.econbiz.de/), the literature search of the ZBW – Leibniz Information Centre for Economics. It lets an AI assistant search economics and business literature, fetch full records, find similar works, check access options and autocomplete terms.

No API key is needed. The API is in beta and has no quota, but it is not meant for bulk copying of EconBiz content (see its [terms of use](https://api.econbiz.de/)).

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
| `query` | Lucene syntax. `AND` is the default operator. Supports `AND`/`OR`/`NOT`, `"phrases"`, fielded search (`title:"knowledge management"`) and `(grouping)`. Special characters must be Lucene-escaped. |
| `size` / `start` | Page size (API default 10) and 1-based position of the first hit |
| `fulltext` | Also search full texts (only partly available) |
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

Requires [uv](https://docs.astral.sh/uv/). No clone is needed: clients run the server straight from GitHub with `uvx`.

```bash
uvx --from git+ssh://git@github.com/mbravidor/econbiz-mcp econbiz-mcp
```

The repository is **private** and the configs use SSH (`git+ssh://`), so the machine needs an SSH key registered with your GitHub account and GitHub in `~/.ssh/known_hosts`. Test `ssh -T git@github.com`. GUI clients start `uvx` without your shell, so also run the command above in a plain terminal first. If the repo is made public, the plain `git+https://github.com/mbravidor/econbiz-mcp` URL works without credentials.

For development, clone the repo and run `uv sync`, then `uv run econbiz-mcp` (it waits for MCP messages on stdin; stop with Ctrl+C).

## Configuration

| Variable | Description |
|---|---|
| `ECONBIZ_APP_NAME` | Short alphanumeric application name, sent as User-Agent. The API terms encourage developers to identify their app. Default `econbizmcp`. |
| `ECONBIZ_PROFILE` | Name of an EconBiz user profile (API `profile` parameter). Leave unset unless you have a registered profile: the API answers `400 Bad Request` to every call with an unknown profile name (tested with `default`, `econbiz`, `portal`). |

## Client setup

Ready-to-use files are in [`configs/`](configs). They run the server from GitHub via `uvx`, so they contain no local paths. To pin a version, append `@v0.1.0` (a git tag) to the URL.

| Client | File | Copy to / merge into |
|---|---|---|
| Claude Code | [`claude-code.json`](configs/claude-code.json) | `.mcp.json` in your project root (or use the command below) |
| Claude Desktop | [`claude-desktop.json`](configs/claude-desktop.json) | Settings → Developer → *Edit Config*. macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`; Windows: `%APPDATA%\Claude\claude_desktop_config.json`. Claude Desktop is not officially available for Linux. |
| opencode | [`opencode.json`](configs/opencode.json) | `opencode.json` in your project, or `~/.config/opencode/opencode.json` globally |
| Zoo Code | [`zoo-code.json`](configs/zoo-code.json) | MCP icon → *Edit Global MCP* (`mcp_settings.json`) or *Edit Project MCP* (`.roo/mcp.json`) |
| Roo Code | [`roo-code.json`](configs/roo-code.json) | Same as Zoo Code |
| Cline | [`cline.json`](configs/cline.json) | MCP Servers → *Configure* → *Configure MCP Servers* (`cline_mcp_settings.json`; the Cline CLI uses `~/.cline/data/settings/cline_mcp_settings.json`) |
| Cursor | [`cursor.json`](configs/cursor.json) | `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global) |
| Windsurf | [`windsurf.json`](configs/windsurf.json) | *Open MCP config file* in the Cascade panel. Current docs name `~/.config/devin/mcp_config.json`; older Windsurf versions used `~/.codeium/windsurf/mcp_config.json` (not re-verified). |
| Gemini CLI | [`gemini-cli.json`](configs/gemini-cli.json) | `mcpServers` key in `.gemini/settings.json` (project) or `~/.gemini/settings.json` (user). The folder must be trusted (`gemini trust`). |
| VS Code (Copilot) | [`vscode.json`](configs/vscode.json) | `.vscode/mcp.json`, or *MCP: Open User Configuration*. VS Code also reads a root `.mcp.json` in the `mcpServers` format, so [`claude-code.json`](configs/claude-code.json) works there too. |

If the target file already exists, merge the `econbiz` entry into the existing server object instead of overwriting the file.

### Format differences between clients

The server definition is the same everywhere (`uvx --from git+ssh://git@github.com/mbravidor/econbiz-mcp econbiz-mcp` plus the `ECONBIZ_APP_NAME` env variable). Only the wrapper differs:

| Client | Top-level key | Command format | Env key | Auto-approve key | `type` |
|---|---|---|---|---|---|
| Claude Code, Claude Desktop, Windsurf, Gemini CLI | `mcpServers` | `command` + `args` | `env` | – (Gemini: `trust: true`) | optional (Claude Code writes `"stdio"`) |
| Cursor | `mcpServers` | `command` + `args` | `env` | – | `"stdio"` (docs table marks it required) |
| Roo Code, Zoo Code | `mcpServers` | `command` + `args` | `env` | `alwaysAllow` | optional, defaults to `stdio` |
| Cline | `mcpServers` | `command` + `args` | `env` | `autoApprove` | not used for stdio |
| VS Code | `servers` | `command` + `args` | `env` | – | `"stdio"` (required) |
| opencode | `mcp` | `command` as one **array** (no `args`) | `environment` | – | `"local"` (required) |

### Claude Code (CLI)

```bash
claude mcp add econbiz --scope user \
  -- uvx --from git+ssh://git@github.com/mbravidor/econbiz-mcp econbiz-mcp
```

### opencode

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "econbiz": {
      "type": "local",
      "command": ["uvx", "--from", "git+ssh://git@github.com/mbravidor/econbiz-mcp", "econbiz-mcp"],
      "enabled": true,
      "environment": {
        "ECONBIZ_APP_NAME": "econbizmcp"
      }
    }
  }
}
```

### Zoo Code / Roo Code (Cline: see note below)

```json
{
  "mcpServers": {
    "econbiz": {
      "command": "uvx",
      "args": ["--from", "git+ssh://git@github.com/mbravidor/econbiz-mcp", "econbiz-mcp"],
      "env": {
        "ECONBIZ_APP_NAME": "econbizmcp"
      },
      "alwaysAllow": ["search", "get_record", "get_availability", "find_similar", "suggest", "list_fields"],
      "disabled": false
    }
  }
}
```

`alwaysAllow` skips the approval prompt for these tools. **Cline names this key `autoApprove`**, so use [`cline.json`](configs/cline.json) for it. All tools are read-only, but remove the entry if you prefer to confirm each call.

### Generic `mcpServers` clients (Claude Desktop, Cursor, Windsurf, Gemini CLI)

```json
{
  "mcpServers": {
    "econbiz": {
      "command": "uvx",
      "args": ["--from", "git+ssh://git@github.com/mbravidor/econbiz-mcp", "econbiz-mcp"],
      "env": {
        "ECONBIZ_APP_NAME": "econbizmcp"
      }
    }
  }
}
```

`claude mcp add` (`--scope user` makes it available in all projects) stores the entry with `"type": "stdio"` and without `ECONBIZ_APP_NAME`. Add `-e ECONBIZ_APP_NAME=...` if you want it.

GUI clients often do not inherit your shell `PATH`. If `uv` is not found, replace `"uvx"` with its absolute path (`which uvx`).

## Example prompts

- "Find recent articles on knowledge management, newest first, and show the top subjects."
- "Which papers by Ikujiro Nonaka are in EconBiz? Filter to 2007."
- "Is record 10015595151 available as free full text? Show similar records by subject."
- "Suggest subject terms starting with *behavioral econ*."

## Development

```bash
uv sync
uv run python -c "import asyncio; from econbiz_mcp import server as s; print(asyncio.run(s.search('inflation', size=1)))"
```

The server is a single file, `src/econbiz_mcp/server.py`, built on the official MCP Python SDK (`FastMCP`, pinned to `mcp<2`) and `httpx`.

## Limitations

- The API is in beta. Only the documented methods and parameters are stable for v1.
- Response bodies are returned as the API sends them. Their structure is only partly documented.
- Full-text search covers only part of the corpus.
- Record IDs must be numeric; anything else is rejected before a request is made.
- A fielded query on a field that does not exist (e.g. `bogus:x`) silently returns 0 hits instead of an error. Check field names with `list_fields`.
- Facet filters accept single values only (`date:2007`); ranges like `date:[2000 TO 2010]` return HTTP 400.
