# Changelog

## 0.1.0

- Initial release: `microsoft-fabric` skill — auth across two token audiences, OneLake file operations via raw REST (no SDK), writing Delta tables locally without a Spark session, CDC-mirroring current-state dedup and its forward-fill fix, cross-tenant governance checklist, troubleshooting reference.
- Adopted two structural conventions from [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric): resolving workspaces/items by listing and filtering rather than guessing GUIDs, and the "terminal write" principle.
- Added `.claude-plugin/marketplace.json` for installation via `/plugin marketplace add` in Claude Code and GitHub Copilot CLI.
