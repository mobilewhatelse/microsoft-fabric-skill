# CDC-mirrored tables: structure, and a critical dedup bug to avoid

Fabric setups that mirror an external database (via Fabric Mirroring, or a custom CDC ingestion pipeline) commonly land data in a **uniform change-event shape** rather than as plain current-state tables. Recognizing this shape — and getting the "collapse history into current state" step right — matters a lot, because getting it wrong produces tables that *look* fine (right row count, right columns) but silently drop real values.

## The shape

Each mirrored source table typically becomes a Delta table where every row is one **change event**, not one current record:

| Column | Meaning |
|---|---|
| `PKs` (struct) | The source table's primary key column(s), nested |
| `details` (struct) | All other business columns, nested |
| `operation` | `INSERT` / `UPDATE` / `DELETE` |
| `operationBy` | Who/what made the change |
| `operationAt` | When (timestamp, or a string like `dd-MM-yyyy HH:mm:ss`) |
| `filename`, `path` | Provenance of the CDC batch |

After flattening the two structs (`PKs.ID` → `PKs_ID`, `details.STATUS` → `details_STATUS`), you get one flat table where **the same source-row can appear many times** — once per historical change.

## Just want to look at a table? Don't reach for the full export pipeline

If the goal is simply "show me this table's real columns so I can eyeball/compare it" — not reconstruct current state, not write anything anywhere — resist the urge to run a full export/dedup/write pipeline for that. Flattening alone is enough, and it has no side effects (no files written, nothing exported):

```python
from pyspark.sql.functions import col, explode_outer, to_json
from pyspark.sql.types import StructType, ArrayType, MapType

def flatten(df, sep="_"):
    while True:
        for f in df.schema.fields:
            if isinstance(f.dataType, MapType):
                df = df.withColumn(f.name, to_json(col(f.name)))
        arr_cols = [f.name for f in df.schema.fields if isinstance(f.dataType, ArrayType)]
        if arr_cols:
            for c in arr_cols:
                df = df.withColumn(c, explode_outer(col(c)))
            continue
        has_struct, exprs = False, []
        for f in df.schema.fields:
            if isinstance(f.dataType, StructType):
                has_struct = True
                for sub in f.dataType.fields:
                    exprs.append(col(f"`{f.name}`.`{sub.name}`").alias(f"{f.name}{sep}{sub.name}"))
            else:
                exprs.append(col(f"`{f.name}`"))
        if not has_struct:
            break
        df = df.select(*exprs)
    return df

def strip_prefix(df, prefixes=("details_", "PKs_")):
    renames = {c: c[len(p):] for c in df.columns for p in prefixes if c.startswith(p)}
    for old, new in renames.items():
        df = df.withColumnRenamed(old, new)
    return df

df = spark.read.format("delta").load(table_path)
df = flatten(df)
df = strip_prefix(df)
display(df)
```

To look at a different table, change `table_path` and re-run — nothing else needed. This still shows every historical CDC event as its own row (not deduplicated to current state) — that's fine for "what columns/values does this table actually have", and you only reach for `is_cdc`/`to_current_state` below once the actual goal is reconstructing one row per entity.

## Detecting it

```python
def is_cdc(df):
    cols = set(df.columns)
    return "PKs" in cols and "details" in cols and "operation" in cols
```

Not every mirrored table is necessarily CDC-shaped — small reference/lookup tables are sometimes landed as plain full snapshots instead. Branch on `is_cdc(df)` per table rather than assuming.

## The bug: "keep the latest row" loses real values

A tempting, simple way to collapse the event history into current state:

```python
# NAIVE — loses data, do not use as-is
from pyspark.sql import Window
from pyspark.sql.functions import col, row_number

w = Window.partitionBy(*pk_cols).orderBy(col("operationAt").desc())
current = (df.filter(col("operation") != "DELETE")
             .withColumn("_rn", row_number().over(w))
             .filter(col("_rn") == 1)
             .drop("_rn"))
```

This looks correct — one row per primary key, the most recent one. **It silently loses data** whenever the CDC stream only ships the columns that actually changed in a given event, leaving unrelated columns `NULL` in that event's row (a very common pattern for log-based CDC / change-stream capture).

Concrete failure: a column gets its only real value at `INSERT` time. A later `UPDATE` event for the *same* primary key changes an unrelated column and carries `NULL` for the first column (because it didn't change). "Keep the latest row" picks that `UPDATE` row — and the earlier, real value for the first column is gone from the output, even though the live source database still has it.

This reproduces reliably any time:
- a column is set once (e.g. at creation) and rarely or never updated again, **and**
- the same entity receives at least one later CDC event for a different field

In practice this tends to hit foreign-key / linking columns hardest, because they're often set once at insert and never touched again — so a table that looks 100% empty for one specific column, while everything else looks populated, is a strong signal to check for exactly this bug rather than assuming the source system never populates that column.

## The fix: forward-fill before picking the latest row

Instead of jumping straight to "keep the latest row", first forward-fill each column's last known non-null value across the entity's full history, *then* keep the latest (now fully reconstructed) row:

```python
from pyspark.sql.functions import col, row_number, first as spark_first, last as spark_last
from pyspark.sql.window import Window

def to_current_state(df, pk_cols):
    df = df.filter(col("operation") != "DELETE")

    reserved = set(pk_cols) | {"operationAt"}
    data_cols = [c for c in df.columns if c not in reserved]

    # Step 1: collapse duplicate events at the exact same (PK, operationAt)
    agg_exprs = [spark_first(col(c), ignorenulls=True).alias(c) for c in data_cols]
    collapsed = df.groupBy(*pk_cols, "operationAt").agg(*agg_exprs)

    # Step 2 (the fix): forward-fill each column's last non-null value,
    # per PK, ordered by time — a running window up to the current row
    fill_window = (Window.partitionBy(*pk_cols)
                   .orderBy(col("operationAt").asc())
                   .rowsBetween(Window.unboundedPreceding, Window.currentRow))
    filled = collapsed
    for c in data_cols:
        filled = filled.withColumn(c, spark_last(col(c), ignorenulls=True).over(fill_window))

    # Step 3: now that every column carries its correct forward-filled value,
    # keep only the newest row per PK
    rank_window = Window.partitionBy(*pk_cols).orderBy(col("operationAt").desc())
    return (filled.withColumn("_rn", row_number().over(rank_window))
                  .filter(col("_rn") == 1)
                  .drop("_rn"))
```

The only structural change versus the naive version is **Step 2** — everything else (dropping deletes, collapsing same-timestamp duplicates, keeping the final latest row, dropping CDC metadata columns afterwards) stays the same. This makes it a safe drop-in replacement in an existing pipeline.

## How to tell if you're affected

For any CDC-mirrored table, check whether a column that's semantically "should basically always have a value" (a foreign key, an amount, a status) comes out **100% null** or suspiciously sparse after your current-state step, while a related field is well populated. If so:

1. Confirm the table is genuinely CDC-shaped (`is_cdc(df)` above).
2. Check whether that column is ever non-null in *any* historical event for affected primary keys (query the raw, pre-dedup event table).
3. If it is, and your dedup only keeps the single latest row, you have this bug — apply the forward-fill fix and re-run.

Fields that were dropped for an unrelated reason (e.g. binary/blob columns explicitly excluded because a downstream format like CSV can't represent them) are a separate, easier-to-diagnose case — check the export/transform logic's column-drop list before assuming it's the CDC dedup bug.
