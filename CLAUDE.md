# Microsoft Fabric Skill Repo

This repo contains skills compatible with both **Claude Code** and **GitHub Copilot**.
Skills live in `.github/skills/<skill-name>/SKILL.md`.

## When adding or modifying skills

Every `SKILL.md` must use **only the frontmatter fields that both Claude Code and GitHub Copilot document**:

```yaml
---
name: microsoft-fabric-<skill-name>
description: <one or two sentences - what it covers and when to invoke it>
license: MIT
---
```

- `name` (must equal the folder name; lowercase letters, digits, hyphens; max 64) and `description` (10-1024 characters, plain single-line text without `: ` or ` #`) are required.
- `license` is optional but harmless.
- **Do not add other fields.** `argument-hint`, `user-invocable`, `disable-model-invocation`, and `allowed-tools` are not understood by every harness; GitHub Copilot does not support them in a skill. `allowed-tools` also pre-approves shell access, which these documentation-only skills do not need. Tools and subagents belong in a custom agent or prompt file, not in a skill.

Run `python tools/check_skills.py` before every commit - it enforces this.

## Structure

Each skill lives in its own subdirectory with a `SKILL.md` entry point and a `references/` folder of focused markdown files. The `SKILL.md` links to the reference files — load only the one relevant to the current task, not all of them upfront.

## Content policy

No organization-specific, project-specific, or customer-specific content — no real workspace/tenant/item IDs, no real table or business-entity names from any client project. Examples use generic placeholders (`<workspace-id>`, `orders`, `customers`, `DEMO-...`) so the skill is safe to reuse anywhere.

## Plugin marketplace — checklist when adding a new skill

This repo is also installable as a Claude Code / GitHub Copilot CLI plugin marketplace via `.claude-plugin/marketplace.json`. That file is the **only** thing that makes a skill folder discoverable through `/plugin install` — adding a new `.github/skills/<name>/` folder is not enough on its own. Whenever a new skill is added (or an existing one meaningfully changes):

1. Add the new skill's folder path to the `skills` array of the `microsoft-fabric` plugin entry in `.claude-plugin/marketplace.json` (one plugin bundles every skill in this repo — don't create a second plugin entry unless the new content is genuinely a separate, independently-installable thing).
2. Bump **both** `version` fields in `marketplace.json` (top-level `metadata.version` and the plugin's own `version`) — this is what lets an existing install's `/plugin update` detect there's something new. Forgetting this means the change ships but nobody with an existing install ever sees it.
3. Add a one-line entry to `CHANGELOG.md` (create it on the first bump if it doesn't exist yet) describing what changed, so someone running `/plugin update` can see why.
4. Update the skill table in `README.md` if a new reference file or skill folder was added.

The plain file-based install paths (Claude Code project `.claude/settings.json`, GitHub Copilot VS Code auto-discovery of `.github/skills/`) don't read `marketplace.json` at all and need no extra step beyond the skill files themselves — the checklist above only matters for the `/plugin marketplace add` + `/plugin install` path.
