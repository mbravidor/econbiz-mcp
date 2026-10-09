# AGENTS.md

MCP server for the EconBiz API v1 (https://api.econbiz.de/). Python, single file: `src/econbiz_mcp/server.py` (official MCP SDK `FastMCP`, `httpx`). Overview and client setup: `README.md`.

## Commands

- Install: `uv sync`
- Run (stdio, waits for MCP messages): `uv run econbiz-mcp`
- There is no test suite. Verify changes against the live API (no key needed), ideally through a real MCP stdio session (`mcp.client.stdio`), not only by calling the functions directly.

## Gotchas

- Keep the dependency pinned to `mcp<2`: v2 renamed `FastMCP` to `MCPServer` and moved the import.
- Do not set `ECONBIZ_PROFILE` when testing: the API returns 400 for every unknown profile name, and no valid name is known.
- Record IDs are numeric digits only; `_record_path` rejects anything else (`..` would otherwise rewrite the URL).
- API quirks: facet filters take single values only (`date:2007`, ranges give 400); an unknown fielded-search field silently returns 0 hits; `size=0` is a valid count-only query. The API is beta, so be gentle (no bulk harvesting).
- Tool parameter names differ from API names (`query`->`q`, `start`->`from`, `filters`->`facet`, `more_like_this`/`similarity`->`mlt`). Keep the mapping table in `README.md` in sync.

## Keeping docs and configs in sync

- Adding or changing a tool or parameter: update the tool docstring (it is what the LLM sees), the README tool tables, and the `alwaysAllow`/`autoApprove` lists in `configs/zoo-code.json`, `roo-code.json` and `cline.json`.
- `configs/*.json` differ per client on purpose: opencode uses `mcp` + a `command` array + `environment`; VS Code uses `servers`; Cline uses `autoApprove`; Roo/Zoo use `alwaysAllow`. Do not "normalize" them. The README embeds these files as snippets, so after editing one, update its snippet in the README `Installation` section (they must be identical; roo-code.json equals zoo-code.json).
- `skills/econbiz-research/SKILL.md` documents search behavior for agents. Update it when tool parameters or verified API quirks change.
- All configs run the server via `uvx --from git+https://github.com/mbravidor/econbiz-mcp`. The repo is public, so no credentials are needed to install.

## Releasing

1. Update `CHANGELOG.md` and bump `version` in `pyproject.toml`.
2. Run `uv lock` so `uv.lock` records the new version.
3. Commit, `git push`, then `git tag -a vX.Y.Z -m "..."` and `git push origin vX.Y.Z`.
4. Check the pinned install: `uvx --refresh --from git+https://github.com/mbravidor/econbiz-mcp@vX.Y.Z econbiz-mcp`.

Ask before pushing or tagging: the repo is public, so pushed commits and tags are visible to everyone and users pin to tags.

## Git

- Remote: `git@github.com:mbravidor/econbiz-mcp.git` (SSH for pushing), branch `main`. Commit identity is set repo-locally.
- Public repo: never commit tokens, personal paths or private data. Commit history is public.
