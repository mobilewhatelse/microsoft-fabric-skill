# Authentication and tokens

Everything in this skill is scripted against Fabric's REST API and OneLake's storage API using the Azure CLI for auth — no Fabric-specific CLI or SDK is required.

## Logging in to a Fabric-only tenant (no Azure subscription)

A Fabric trial or a Fabric-only account often has **no Azure subscription** attached. Plain `az login` may warn or behave oddly in that case. Use:

```bash
az login --use-device-code --allow-no-subscriptions
```

`--use-device-code` prints a URL + short code to visit in any browser (useful when the shell itself has no browser, or when you want to log in as a *different* account than whatever is already cached). `--allow-no-subscriptions` stops the CLI from erroring out when the tenant has zero Azure subscriptions — normal for a Fabric-only trial.

Verify who's active:

```bash
az account show
```

If you need to switch between multiple logged-in identities (e.g. a work tenant and a personal trial tenant), `az login` again with a different account — each login adds/overwrites the relevant token cache entry; `az account show` always reflects the most recently completed login.

## Two different token audiences

Fabric splits its surface across two distinct APIs, each requiring a token issued for a **different resource/audience**. Requesting a token for the wrong one produces confusing 401/403s that look like a permissions problem but are actually just the wrong audience.

| API surface | Resource for `--resource` | Used for |
|---|---|---|
| Fabric REST API | `https://api.fabric.microsoft.com` | Listing/creating workspaces, items (Lakehouse, Notebook, Warehouse, ...), running notebook/pipeline jobs |
| OneLake (ADLS Gen2 surface) | `https://storage.azure.com` | Reading/writing/listing files and folders inside a Lakehouse's `Files`/`Tables` area |

```bash
# Fabric REST API token
az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv

# OneLake file-system token
az account get-access-token --resource https://storage.azure.com --query accessToken -o tsv
```

Both tokens are short-lived (roughly 60–90 minutes). Re-fetch rather than trying to refresh — it's a single CLI call and there's no reason to cache it to disk.

## Minimal smoke test

```bash
TOKEN=$(az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv)
curl -s -H "Authorization: Bearer $TOKEN" "https://api.fabric.microsoft.com/v1/workspaces"
```

A `200` with a `{"value": [...]}` list of workspaces confirms the identity, tenant, and token audience are all correct before building anything more complex on top.
