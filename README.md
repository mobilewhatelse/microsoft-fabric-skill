# Microsoft Fabric Skills — Claude Code + GitHub Copilot

A skill collection compatible with both **[Claude Code](https://claude.com/claude-code)** and **[GitHub Copilot](https://github.com/features/copilot)**, packaging field-tested, copy-pasteable patterns for scripting **Microsoft Fabric** — workspaces, Lakehouses, OneLake, and CDC-mirrored data — directly against its REST APIs.

No project-specific or organization-specific content — just the mechanics of the platform, distilled from real end-to-end sessions.

Note: Microsoft Fabric is its own product line, separate from the "Power Platform" (Power Apps, Power Pages, Copilot Studio). See [github.com/mobilewhatelse/power-platform-skill](https://github.com/mobilewhatelse/power-platform-skill) for that side.

## Using these skills

### Claude Code
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
| [`auth-and-tokens.md`](.github/skills/microsoft-fabric/references/auth-and-tokens.md) | Device-code login without an Azure subscription, the two token audiences (Fabric REST API vs. OneLake), a minimal smoke test |
| [`onelake-rest-api.md`](.github/skills/microsoft-fabric/references/onelake-rest-api.md) | Upload (create/append/flush), the List Paths URL-shape gotcha, delete, Windows argument-length note |
| [`delta-tables-without-spark.md`](.github/skills/microsoft-fabric/references/delta-tables-without-spark.md) | Writing valid Delta tables locally with `deltalake` + `pyarrow`, no Spark/Java required |
| [`cdc-mirroring-and-dedup.md`](.github/skills/microsoft-fabric/references/cdc-mirroring-and-dedup.md) | The `PKs`/`details`/`operation`/`operationAt` shape, the "keep latest row" dedup bug that silently drops real values, and the forward-fill fix |
| [`governance-and-tenants.md`](.github/skills/microsoft-fabric/references/governance-and-tenants.md) | What gets audit-logged, a checklist before any cross-tenant shortcut/copy, what to do if real data ends up somewhere it shouldn't |
| [`troubleshooting.md`](.github/skills/microsoft-fabric/references/troubleshooting.md) | Error messages → causes → fixes |

## Core principle

Script the Fabric REST API and OneLake's storage API directly rather than clicking through the portal UI. Authenticate on demand with `az account get-access-token` (never persist tokens to disk), and prefer generating structurally-realistic synthetic data over copying real data across workspace/tenant boundaries.

## Using a skill

Copy the relevant `skills/<name>/` directory into a Claude Code skills directory (project-local `.claude/skills/` or a plugin), or point Claude Code at this repo. Each skill's `SKILL.md` is the entry point; it loads only the reference docs relevant to the current task.

## License

MIT — see [LICENSE](LICENSE).
