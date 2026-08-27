# Writing real Delta tables without a Spark session

You don't need a running Fabric notebook / Spark cluster to produce a valid Delta table that `spark.read.format("delta").load(...)` can read. The Python package **`deltalake`** (a `delta-rs` binding) plus **`pyarrow`** write the real Delta Lake file format — a `_delta_log/` folder of commit JSON files next to Parquet data files — entirely locally.

This is useful for:
- Seeding a Lakehouse with test/demo data that must look like a genuine Delta table (not just a CSV in `Files/`)
- Building fixtures that exercise a specific downstream transform (e.g. a CDC merge/dedup notebook) without needing the real source system or a live notebook run
- Any scripted Fabric setup where spinning up a Spark session just to write a handful of rows would be wasteful

## Install

```bash
pip install deltalake pyarrow
```

No Java, no Spark, no Hadoop winutils — pure Python/Rust.

## Write a table

```python
import pyarrow as pa
from deltalake import write_deltalake

data = {
    "id": ["1", "2", "3"],
    "name": ["Alpha", "Beta", "Gamma"],
    "amount": ["100.0", "250.5", "75.25"],
}
table = pa.table({k: pa.array(v, type=pa.string()) for k, v in data.items()})

write_deltalake("/local/path/my_table", table, mode="overwrite")
```

This produces:

```
my_table/
├── _delta_log/
│   └── 00000000000000000000.json
└── part-00000-<uuid>-c000.snappy.parquet
```

`mode="overwrite"` replaces the table cleanly on repeated runs (useful while iterating on a generator script). Reading it back (still without Spark, useful for verifying before uploading anywhere):

```python
from deltalake import DeltaTable
df = DeltaTable("/local/path/my_table").to_pandas()
```

## Getting it into a Fabric Lakehouse

Upload the whole local folder tree (every file under `_delta_log/` and every `*.parquet` part file) to `Files/<name>/` in the target Lakehouse via the OneLake REST API — see [onelake-rest-api.md](onelake-rest-api.md). A Fabric notebook can then do exactly:

```python
df = spark.read.format("delta").load("Files/<name>")
```

and it will read your locally-built table with no indication it wasn't written by Spark.

## Practical tips

- **Everything as strings is fine for fixtures.** If the downstream consumer (e.g. a notebook expecting a specific schema) tolerates string-typed columns, skip type inference entirely — it avoids a whole class of "why did this column become a float with `.0` suffix" surprises. Cast explicitly only where the consumer genuinely needs a non-string type.
- **Match the exact folder-naming convention the consumer expects.** If a downstream script does something like `folder_name.replace("tableName=", "")` to derive a table name, name your local output folder `tableName=<name>` so the unmodified script works against your fixture without edits.
- **Composite primary keys** are just multiple columns — nothing special needed at the Delta-writing level; only matters once a downstream `GROUP BY`/`PARTITION BY` on those columns runs.
