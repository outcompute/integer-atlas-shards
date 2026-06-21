# Shards repo — process

This repo houses **work orders** and **manifests** — nothing else. Manifests are
pointers to shard files stored elsewhere. The CLI reads these directories directly
(shallow clone or tarball); there is no compiled index, no published site, no packs
registry, no dataset-release machinery.

## Directories

| Dir | Holds | Written by |
| --- | --- | --- |
| `pending/` | work orders (a range + columns + algo release to compute) | maintainer (drops in a JSON file) |
| `computed/` | submitted manifests awaiting verification | contributor (PR) |
| `accepted/` | verified manifests = the live dataset pointers | the promote step (on merge) |

One JSON file per shard/work-order, so PRs touch disjoint files. `schema/` validates
both shapes.

## Branches

- **`main` only.** All PRs target `main` (protected: PR checks + one review).
- No other long-lived branches, no GitHub Pages branch. **Don't pre-create branches** —
  contributors use an ephemeral fork/branch per submission.
- **Snapshots are free via git:** any commit or tag is an immutable, reproducible view.
  The CLI's `--release` pins a git ref (e.g. a tag like `2026.06`). No release pipeline.

## Contributor flow

1. Compute + upload the shard; `integer-atlas submit` produces the manifest + PR body.
2. Open a PR adding `computed/<…>.json` and removing the `pending/<…>.json` it fills.
3. `pr-validate.yml`: schema-check, then download the shard, match hashes, and
   `atlas-algos verify` at the pinned `algorithm_release`.
4. A maintainer reviews and merges. `promote.yml` flips status to `accepted` and moves
   the file `computed/ → accepted/`.

## Work orders

A maintainer authors work orders as JSON files in `pending/` (a range, the columns to
compute, and the algorithm release). `scripts/plan.py` generates them by tiling a range
into uniform shard-sized cells:

```
python scripts/plan.py --start 1 --end 1000000 --shard-size 1000000 \
  --columns "$(atlas-algos columns --csv)" --algorithm-release algos-0.1.0
```

## Collisions

There is no formal claiming: two people computing the same range produce overlapping
`accepted/` entries or conflict on the same `pending/` removal, which surfaces the
duplication in review.

## How the CLI consumes this repo

`integer-atlas` shallow-clones (or tarball-downloads) the repo into its cache and reads
`accepted/` for available shards and `pending/` for the work list. `--registry` points
at a fork; `--release <ref>` pins a git ref. That's the entire contract.
