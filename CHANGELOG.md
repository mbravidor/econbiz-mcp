# Changelog

## 0.2.0
- Added the optional `skills/econbiz` agent skill (query syntax, recall pitfalls).
- Tool docstrings now cover wildcards, date ranges in queries, language codes, `fulltext` semantics and the first-author-only `creator` field.
- README: documented the same behaviors.

## 0.1.1
- Exit cleanly (code 0, no traceback) on Ctrl+C.
- README: note that the server starts silently and waits on stdin.
- Hardened HTTP layer: shared client, redirects, clear errors for network failures and non-JSON replies, numeric-only record IDs, empty parameter values dropped.
- Added AGENTS.md / CLAUDE.md.

## 0.1.0
- Initial release: tools `search`, `get_record`, `get_availability`, `find_similar`, `suggest`, `list_fields`; ready-made configs for ten MCP clients.
