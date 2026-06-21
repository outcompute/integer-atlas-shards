# Integer Atlas — Shards

A pointer store. It houses **work orders** and **manifests** — small JSON files. It holds
**no large data**; manifests point at shard files stored elsewhere (object storage,
Kaggle, mirrors). The CLI reads these directories directly.

## Layout

```
pending/      work orders: a range + columns + algorithm release to compute   [work-order schema]
computed/     submitted manifests awaiting verification (contributor PRs land here)
accepted/     verified manifests = the live dataset pointers
schema/       manifest.schema.json, work-order.schema.json
scripts/      validate (schema) · verify (download + hashes + atlas-algos) · promote (computed→accepted)
.github/workflows/   pr-validate · promote
```

One JSON file per shard/work-order. State = which directory it's in.

## A manifest is just a pointer

```json
{
  "file": "pos_…_numbers_factor_….parquet",
  "range_start": 1, "range_end": 10000000, "row_count": 10000000,
  "columns": [ { "name": "is_prime", "type": "boolean" } ],
  "format": "parquet",
  "algorithm_release": "algos-0.1.0",
  "hashes": { "sha256": "…", "sha512": "…", "blake3": "…" },
  "storage": [ "https://…/the-shard.parquet" ],
  "verification": { "status": "accepted", "degree": 0.1 }
}
```

That's everything the CLI needs to fetch, verify, and load the shard. The
`algorithm_release` ties it back to the Algos repo tag that produced it.

## Process & consumption

Branches, PR flow, and how the CLI reads the repo are in **[PROCESS.md](PROCESS.md)**.
In short: one `main` branch; contributor PRs add `computed/…`; CI validates + verifies;
merge → promote to `accepted/`. The CLI shallow-clones the repo and reads `accepted/`
(data) and `pending/` (work); `--release` pins a git ref for a reproducible snapshot.

No index file, no published site, no packs registry, no dataset-release machinery — git
and the directories are the whole system.
