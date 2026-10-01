# Contributing to Microsoft Fabric Skills

Thanks for helping. This repository holds skills for **Claude Code** and **GitHub Copilot**. The same files must load unchanged in both, so a few rules are strict. Please read this page before adding or changing a skill.

## Adding a skill

1. **Create the folder** `.github/skills/microsoft-fabric-<topic>/` with a `SKILL.md` entry point and a `references/` folder of focused markdown files. The folder name is the skill name.
2. **Write the frontmatter with exactly these fields** (nothing else):

```yaml
---
name: microsoft-fabric-<topic>
description: <one or two sentences - what it covers and when to invoke it>
license: MIT
---
```

   - `name` must equal the folder name: lowercase letters, digits, and hyphens, at most 64 characters.
   - `description` is 10-1024 characters, a single line, and must not contain `: ` or ` #` (that breaks plain YAML). Say what the skill covers **and when to use it** - this text decides whether an assistant loads it.
   - `license` is optional.
3. **Keep `SKILL.md` short.** It states when to use the skill, the workflow, and the core principles, and links to the reference files. Details, snippets, and tables go into `references/*.md` so an assistant loads only what the task needs.
4. **Register the skill** (only needed for installation through the plugin marketplace):
   - add the folder to the `skills` array of the `microsoft-fabric` plugin entry in `.claude-plugin/marketplace.json`,
   - raise **both** `version` fields (`metadata.version` and the plugin's `version`): minor for a new skill, patch for a fix,
   - add a line to `CHANGELOG.md`,
   - update the skill table in `README.md`.
5. **Run the checks** before you commit:

   ```
   python tools/check_skills.py
   ```

## Why only three frontmatter fields

GitHub Copilot documents `name`, `description`, and `license` (and `allowed-tools` as plain text) for a skill; fields such as `argument-hint`, `user-invocable`, or `disable-model-invocation` are not supported there, and a user reported that skills carrying them did not work in Copilot. `allowed-tools` would also pre-approve shell access, which documentation-only skills do not need. Keep the portable set.

## Tools and subagents do not belong in a skill

A skill is on-demand knowledge. It cannot restrict tools or start subagents. If you need a fixed tool set or a helper agent, put that in a custom agent (`.github/agents/*.agent.md`, fields `tools`, `agents`) or a prompt file (`.github/prompts/*.prompt.md`) that uses the skill.

## Content policy

These repositories are public and reusable. Do not include:

- user names, e-mail addresses, passwords, tokens, or other credentials,
- organization, customer, project, or environment names, and real identifiers (IDs, GUIDs, domains, IP addresses),
- screenshots or exports of a real environment.

Use placeholders (for example `<workspace-id>` or `Firstname Lastname`) and write what you learned as general mechanics, not as a story about one project.

## Commits

Please use an anonymous or noreply e-mail address for commits to these public repositories.

## Pull request checklist

- [ ] Frontmatter has only `name`, `description`, `license`, and `tools/check_skills.py` passes
- [ ] No names, addresses, credentials, environment identifiers, or links to a real environment
- [ ] Skill registered in `marketplace.json`, both versions raised, `CHANGELOG.md` and the README table updated
