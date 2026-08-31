# Microsoft Fabric Skills — Claude Code + GitHub Copilot

A skill collection compatible with both **[Claude Code](https://claude.com/claude-code)** and **[GitHub Copilot](https://github.com/features/copilot)**, packaging field-tested, copy-pasteable patterns for scripting **Microsoft Fabric** — workspaces, Lakehouses, OneLake, and CDC-mirrored data — directly against its REST APIs.

No project-specific or organization-specific content — just the mechanics of the platform, distilled from real end-to-end sessions.

Note: Microsoft Fabric is its own product line, separate from the "Power Platform" (Power Apps, Power Pages, Copilot Studio). See [github.com/mobilewhatelse/power-platform-skill](https://github.com/mobilewhatelse/power-platform-skill) for that side.

## Relationship to Microsoft's official skills

Microsoft publishes a much larger, officially maintained skill collection at **[microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric)** (25 skills covering SQL Warehouse, Spark/Lakehouse notebooks, Power BI, Eventhouse/KQL, Eventstreams, Dataflows Gen2, migrations, and more — installable as a Claude Code / Copilot CLI plugin marketplace). For broad Fabric work, install that first.

This repo is a **narrow complement**, not a competing general-purpose collection — it covers a few specific gaps found while doing real Fabric work that the official skills don't (as of this writing): scripting OneLake file operations with plain REST calls (no SDK, no Spark session involved at all), writing valid Delta tables entirely locally, and a specific CDC-mirroring dedup bug. Two structural conventions here were adopted from the official repo's design: resolving workspaces/items by listing and filtering rather than guessing GUIDs, and the "terminal write" principle (an action isn't done until the state-changing call actually ran and was confirmed) — see [`auth-and-tokens.md`](.github/skills/microsoft-fabric/references/auth-and-tokens.md).

## Using these skills

### Claude Code CLI / GitHub Copilot CLI (plugin marketplace)
```
/plugin marketplace add mobilewhatelse/microsoft-fabric-skill
/plugin install microsoft-fabric@microsoft-fabric-skill
```
Gets you an update command (`/plugin update`) and version tracking — see [CHANGELOG.md](CHANGELOG.md) for what changed between versions.

### Claude Code (file-based, no plugin install)
Add this repo as a skills source in your project's `.claude/settings.json`, or reference individual skill files directly in chat. Skills are in `.github/skills/<skill-name>/SKILL.md`.

### GitHub Copilot (VS Code)
Clone or add this repo. Copilot auto-discovers skills from `.github/skills/` and makes them available as slash commands (e.g. `/microsoft-fabric`). Requires VS Code with GitHub Copilot extension in agent mode.

### Both
Skills use a shared `SKILL.md` format — `name`, `description`, and content work identically in both tools. Copilot-specific fields (`allowed-tools`, `argument-hint`, `user-invocable`) are ignored by Claude Code.

## Skills in this repo

### `microsoft-fabric` — Workspaces, Lakehouses, OneLake, CDC-mirrored data

For scripting **Microsoft Fabric** without the portal UI, a Spark session, or a dedicated Fabric CLI — authentication across two different token audiences, OneLake file operations via the raw ADLS Gen2 REST API, writing real Delta tables locally with `deltalake`/`pyarrow`, recognizing CDC-mirrored table structure and a specific dedup bug that silently drops real data, and cross-tenant governance caution.

Entry point: [`.github/skills/microsoft-fabric/SKILL.md`](.github/skills/microsoft-fabric/SKILL.md)

| Reference | Content |
|---|---|
| [`auth-and-tokens.md`](.github/skills/microsoft-fabric/references/auth-and-tokens.md) | Device-code login without an Azure subscription, the two token audiences (Fabric REST API vs. OneLake), a minimal smoke test, resolving workspaces/items without guessing GUIDs, the "terminal write" principle |
| [`onelake-rest-api.md`](.github/skills/microsoft-fabric/references/onelake-rest-api.md) | Upload (create/append/flush), the List Paths URL-shape gotcha, delete, Windows argument-length note |
| [`delta-tables-without-spark.md`](.github/skills/microsoft-fabric/references/delta-tables-without-spark.md) | Writing valid Delta tables locally with `deltalake` + `pyarrow`, no Spark/Java required |
| [`cdc-mirroring-and-dedup.md`](.github/skills/microsoft-fabric/references/cdc-mirroring-and-dedup.md) | The `PKs`/`details`/`operation`/`operationAt` shape, raw-batch-files vs. consolidated-table layers, the "keep latest row" dedup bug and its forward-fill fix (plus a `StackOverflowError` caveat on wide tables), a `strip_prefix` business/metadata-column collision, and a multi-table value-scan pattern |
| [`governance-and-tenants.md`](.github/skills/microsoft-fabric/references/governance-and-tenants.md) | What gets audit-logged, a checklist before any cross-tenant shortcut/copy, what to do if real data ends up somewhere it shouldn't, and why workspace role alone doesn't guarantee item-creation rights |
| [`troubleshooting.md`](.github/skills/microsoft-fabric/references/troubleshooting.md) | Error messages → causes → fixes |

## Core principles

- Script the Fabric REST API and OneLake's storage API directly rather than clicking through the portal UI. Authenticate on demand with `az account get-access-token` (never persist tokens to disk).
- Resolve workspaces and items by listing and filtering by name — never hard-code or guess a GUID.
- An action isn't done until the state-changing call actually ran and its result was confirmed — describing or printing what *should* happen is not the same as making it happen.
- Prefer generating structurally-realistic synthetic data over copying real data across workspace/tenant boundaries.

## Using a skill

Copy the relevant `skills/<name>/` directory into a Claude Code skills directory (project-local `.claude/skills/` or a plugin), or point Claude Code at this repo. Each skill's `SKILL.md` is the entry point; it loads only the reference docs relevant to the current task.

## License

MIT — see [LICENSE](LICENSE).
