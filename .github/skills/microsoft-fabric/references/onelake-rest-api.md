# OneLake file operations via REST (no SDK needed)

OneLake exposes an **ADLS Gen2**-compatible Data Lake Storage REST API. You don't need `azure-storage-file-datalake` or any other SDK — plain `requests`/`curl` calls work, authenticated with a `https://storage.azure.com` token (see [auth-and-tokens.md](auth-and-tokens.md)).

## URL shape

```
https://onelake.dfs.fabric.microsoft.com/<workspaceId>/<itemId>/<path>
```

- `workspaceId` — the Fabric workspace GUID
- `itemId` — the GUID of the Lakehouse (or other OneLake-backed item) *inside* that workspace — not the workspace's own default filesystem name
- `path` — usually starts with `Files/...` or `Tables/...`

Get both GUIDs from the Fabric REST API first:

```bash
curl -s -H "Authorization: Bearer $FABRIC_TOKEN" \
  "https://api.fabric.microsoft.com/v1/workspaces/<workspaceId>/items"
```

## Uploading a file (create → append → flush)

ADLS Gen2's write path is a three-call sequence — there's no single "PUT this file" call for files with actual content:

```bash
BASE="https://onelake.dfs.fabric.microsoft.com/<workspaceId>/<itemId>"
PATH="Files/demo/example.csv"
HEADERS=(-H "Authorization: Bearer $STORAGE_TOKEN" -H "x-ms-version: 2021-08-06")

# 1) Create the (empty) file
curl -s -X PUT "${HEADERS[@]}" "$BASE/$PATH?resource=file"

# 2) Append the actual bytes at offset 0
curl -s -X PATCH "${HEADERS[@]}" -H "Content-Type: application/octet-stream" \
  "$BASE/$PATH?action=append&position=0" --data-binary @local-file.csv

# 3) Flush — makes the appended bytes visible, must state the total length written
SIZE=$(stat -c%s local-file.csv)
curl -s -X PATCH "${HEADERS[@]}" "$BASE/$PATH?action=flush&position=$SIZE"
```

In Python (`requests`), the same three calls:

```python
import requests

def upload_file(base_url, path, local_bytes, token):
    headers = {"Authorization": f"Bearer {token}", "x-ms-version": "2021-08-06"}
    url = f"{base_url}/{path}"

    r = requests.put(url, headers=headers, params={"resource": "file"})
    r.raise_for_status()

    r = requests.patch(url, headers={**headers, "Content-Type": "application/octet-stream"},
                        params={"action": "append", "position": "0"}, data=local_bytes)
    r.raise_for_status()

    r = requests.patch(url, headers=headers, params={"action": "flush", "position": str(len(local_bytes))})
    r.raise_for_status()
```

For a whole local folder tree (e.g. a Delta table's `_delta_log/` + parquet parts, see [delta-tables-without-spark.md](delta-tables-without-spark.md)), walk the tree and call this once per file, preserving the relative path under the destination prefix. There's no native "upload directory" call.

## Listing paths — the gotcha

The natural-looking URL (workspace **and** item as path segments, then `?resource=filesystem&directory=...`) returns confusing, wrong results (e.g. the Lakehouse's own top-level folder names instead of your target subfolder). The **filesystem** in ADLS Gen2 terms is the *workspace*; the item and its internal path are the `directory` query parameter, not extra path segments:

```bash
# WRONG — looks plausible, silently lists the wrong thing
curl -s -H "Authorization: Bearer $STORAGE_TOKEN" \
  "https://onelake.dfs.fabric.microsoft.com/<workspaceId>/<itemId>?recursive=false&resource=filesystem&directory=Files/demo"

# RIGHT — workspace only in the path, item+path folded into `directory`
curl -s -H "Authorization: Bearer $STORAGE_TOKEN" \
  "https://onelake.dfs.fabric.microsoft.com/<workspaceId>?resource=filesystem&recursive=true&directory=<itemId>/Files/demo"
```

The response is `{"paths": [{"name": "...", "contentLength": N, "isDirectory": true|false}, ...]}`, with `name` values already relative to the workspace root (i.e. they include the `<itemId>/...` prefix).

## Deleting a folder

```bash
curl -s -X DELETE -H "Authorization: Bearer $STORAGE_TOKEN" -H "x-ms-version: 2021-08-06" \
  "https://onelake.dfs.fabric.microsoft.com/<workspaceId>/<itemId>/Files/demo?recursive=true"
```

Always verify with a List Paths call afterwards — a `200` on delete doesn't by itself prove the tree is gone if the path was wrong.

## Windows note

If building a large multi-column `curl`/`psql`-style command inline as a single CLI argument, watch for OS argument-length limits (see [troubleshooting.md](troubleshooting.md)) — prefer piping the body/SQL via stdin over passing it as a giant `-c`/`--data` argument.
