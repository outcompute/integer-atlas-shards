# Shards repo — process

This repo houses **work orders** and **manifests** — nothing else. Manifests are
pointers to shard files stored elsewhere. The CLI reads these directories directly
(shallow clone or tarball); there is no compiled index, no published site, no packs
registry, no dataset-release machinery.

## Directories

| Dir | Holds | Written by |
| --- | --- | --- |
| `pending/` | work orders (a range + columns to compute) | maintainer (drops in a JSON file) |
| `accepted/` | verified manifests = the live dataset pointers | contributor (PR, gated by CI) |

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
2. Open a PR adding `accepted/<table>/<id>.json` (and removing the `pending/<id>.json` it
   fills).
3. `pr-validate.yml` schema-checks every manifest, then for the manifest(s) the PR adds,
   downloads the shard, matches hashes, and runs `atlas-algos verify` at the manifest's
   `algorithm_release`.
4. A maintainer merges once CI is green — the manifest is live immediately. There is no
   separate promote step: the `accepted/` directory is the source of truth.

## Work orders

A maintainer authors work orders as JSON files in `pending/` (a range and the columns to
compute). `scripts/plan.py` generates them by tiling a range into uniform shard-sized
cells. Install the script dependencies first (`pip install -r scripts/requirements.txt`):

```
python scripts/plan.py --start 1 --end 1000000 --shard-size 1000000 \
  --columns "$(atlas-algos columns --csv)" --table core
```

Use `--table <group>` to name a column group when you split columns across shards. Work
orders carry no algorithm version — `atlas-algos` stamps each manifest with its own
version at compute time.

## Collisions

There is no formal claiming: two people computing the same range produce overlapping
`accepted/` entries or conflict on the same `pending/` removal, which surfaces the
duplication in review.

## How the CLI consumes this repo

`integer-atlas` shallow-clones (or tarball-downloads) the repo into its cache and reads
`accepted/` for available shards and `pending/` for the work list. `--registry` points
at a fork; `--release <ref>` pins a git ref. That's the entire contract.
