---
name: microsoft-fabric
description: Script Microsoft Fabric via its REST API and OneLake's storage API - authenticate without an Azure subscription, upload/list/delete files in a Lakehouse, write real Delta tables without a Spark session, recognize CDC-mirrored table structure and its critical dedup bug, and cross-tenant governance caution. Use when the user is working with a Fabric workspace, Lakehouse, OneLake, mirrored/CDC data, or building synthetic test data for a Fabric pipeline.
allowed-tools: [shell]
argument-hint: "which workspace/lakehouse are you working on, and is the data real or does it need to be synthetic?"
user-invocable: true
---

# Microsoft Fabric

This skill packages field-tested patterns for scripting **Microsoft Fabric** — workspaces, Lakehouses, OneLake — directly against its REST APIs, without needing the Fabric portal UI, a running Spark session, or a dedicated Fabric CLI.

It contains no organization-specific or customer-specific content — only the mechanics of the platform.

## When to use this

- You need to **authenticate** to a Fabric workspace or tenant from a script, including a Fabric-only trial tenant with no Azure subscription. See [references/auth-and-tokens.md](references/auth-and-tokens.md).
- You need to **upload, list, or delete files** in a Lakehouse's `Files`/`Tables` area from outside the Fabric portal (e.g. from a CI job, a local script, or an agent). See [references/onelake-rest-api.md](references/onelake-rest-api.md).
- You need to **seed a Lakehouse with realistic test data** — including proper Delta-format tables — without spinning up a Spark session. See [references/delta-tables-without-spark.md](references/delta-tables-without-spark.md).
- You're working with a table that came from **Fabric Mirroring or a CDC pipeline** (columns like `PKs`, `details`, `operation`, `operationAt`) and a column that should have a value is unexpectedly `NULL` — see [references/cdc-mirroring-and-dedup.md](references/cdc-mirroring-and-dedup.md) for a very specific, easy-to-reproduce dedup bug and its fix.
- You're about to create a **OneLake shortcut or copy that crosses a workspace/tenant boundary**, especially involving anything that might be real business/customer data — see [references/governance-and-tenants.md](references/governance-and-tenants.md) first.
- Something errors and you're not sure if it's a Fabric REST API problem or a OneLake file problem — see [references/troubleshooting.md](references/troubleshooting.md).

## Prerequisites

- Azure CLI (`az`) — used for all authentication, no separate Fabric CLI required.
- Python with `requests` for REST calls, and optionally `deltalake` + `pyarrow` if writing Delta tables locally.
- A Fabric workspace you have at least Contributor access to (a free trial workspace is enough for everything in this skill).

## Workflow

1. **Authenticate** — get the right token for the right API surface (Fabric REST vs. OneLake are two different audiences). See [references/auth-and-tokens.md](references/auth-and-tokens.md).
2. **Discover** what already exists before creating anything — `GET /v1/workspaces` and `GET /v1/workspaces/{id}/items` to find existing Lakehouses/Warehouses rather than assuming a fresh empty workspace.
3. **Read or write files** in a Lakehouse via the OneLake REST API — same auth, different resource audience and URL shape than the Fabric API itself. See [references/onelake-rest-api.md](references/onelake-rest-api.md).
4. **Building test/demo data?** Prefer generating structurally-realistic synthetic data (real column names and types, fabricated values) over copying or shortcutting real data — see [references/delta-tables-without-spark.md](references/delta-tables-without-spark.md) and, before crossing any tenant boundary at all, [references/governance-and-tenants.md](references/governance-and-tenants.md).
5. **Working with mirrored/CDC data?** Confirm whether a table is CDC-shaped before writing any "collapse to current state" logic, and specifically watch for the forward-fill dedup bug — it's easy to write and easy to miss. See [references/cdc-mirroring-and-dedup.md](references/cdc-mirroring-and-dedup.md).

Each reference file is self-contained with working request/response shapes and copy-pasteable snippets — read the one relevant to the task at hand rather than all of them up front.

## Core principle: script the REST APIs, don't rely on the portal UI or a Fabric-specific CLI

Every operation in this skill (workspace/item discovery, file upload/list/delete, Delta table creation) is a plain HTTP call authenticated with a short-lived bearer token from:

```bash
az account get-access-token --resource <api.fabric.microsoft.com | storage.azure.com> --query accessToken -o tsv
```

Never persist that token to disk — fetch it fresh at the start of each script run. This means scripts built with this skill contain zero secrets and are safe to commit to source control as-is.

Two more rules that apply across every reference in this skill:

- **Never guess a workspace or item GUID.** Resolve it by listing and filtering by display name (see [references/auth-and-tokens.md](references/auth-and-tokens.md)) — a GUID copied from an old URL or screenshot silently points at the wrong (or a deleted) item.
- **"Terminal write": an action isn't done until the state-changing call actually ran and its result was confirmed.** Printing a payload, a file's content, or "here's what I would run" is not the same as making the change — and where practical, read the result back afterward (list the file, re-fetch the item) rather than trusting the write call's status code alone.
