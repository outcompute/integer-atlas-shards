# Integer Atlas — Shards

A pointer store. It houses **work orders** and **manifests** — small JSON files. It holds
**no large data**; manifests point at shard files stored elsewhere (object storage,
Kaggle, mirrors). The CLI reads these directories directly.

## Layout

```
pending/      work orders: a range + columns to compute   [work-order schema]
accepted/     verified manifests = the live dataset pointers (contributor PRs add here)
schema/       manifest.schema.json, work-order.schema.json
scripts/      validate (schema) · verify (download + hashes + atlas-algos) · plan (work orders)
.github/workflows/   pr-validate
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
In short: one `main` branch; a contributor PR adds the manifest straight to `accepted/`;
CI validates the schema and independently verifies the shard; merge makes it live. The
CLI shallow-clones the repo and reads `accepted/` (data) and `pending/` (work);
`--release` pins a git ref for a reproducible snapshot.

No index file, no published site, no packs registry, no dataset-release machinery — git
and the directories are the whole system.

## License & citation

- **Code** (the scripts here) — MIT, see [LICENSE](LICENSE).
- **Data** (the shards these manifests point to) — **CC BY 4.0**, see [LICENSE-DATA](LICENSE-DATA): use it for anything, including commercially; just attribute. Each manifest also carries `"license": "CC-BY-4.0"`.
- **Citation** — see [CITATION.cff](CITATION.cff) (GitHub's "Cite this repository").
