# Changelog

## 0.2.0

- `cdc-mirroring-and-dedup.md`: added the raw-batch-files vs. consolidated-Delta-table architecture split (Avro/JSON per-batch landing folder vs. the merged CDC table), with the diagnostic technique of checking the raw layer to tell "source never sent it" from "consolidation lost it".
- `cdc-mirroring-and-dedup.md`: documented a `strip_prefix` collision gotcha — a business column (e.g. `details_FILENAME`) can collide case-insensitively with a CDC metadata column (`filename`) after stripping, causing `AnalysisException [AMBIGUOUS_REFERENCE]`; updated the reference `strip_prefix` to detect and suffix on collision.
- `cdc-mirroring-and-dedup.md`: added a "scanning every table and column for a value" section — a two-pass (combined-filter-then-per-column) search pattern, and the lesson that a per-table try/except in a multi-table loop must wrap the whole read+transform pipeline, not just the read call.

## 0.1.0

- Initial release: `microsoft-fabric` skill — auth across two token audiences, OneLake file operations via raw REST (no SDK), writing Delta tables locally without a Spark session, CDC-mirroring current-state dedup and its forward-fill fix, cross-tenant governance checklist, troubleshooting reference.
- Adopted two structural conventions from [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric): resolving workspaces/items by listing and filtering rather than guessing GUIDs, and the "terminal write" principle.
- Added `.claude-plugin/marketplace.json` for installation via `/plugin marketplace add` in Claude Code and GitHub Copilot CLI.
