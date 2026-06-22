"""Generate work orders: tile [start, end] by shard size, one JSON file per cell.

The column list is supplied explicitly (e.g. from `atlas-algos columns --csv`), so the
planner stays decoupled from the Algos toolchain. Each emitted file follows
schema/work-order.schema.json. Re-running overwrites by id (idempotent for a fixed grid).

  python scripts/plan.py --start 1 --end 1000000 --shard-size 1000000 \
    --columns "$(atlas-algos columns --csv)" --table core

Work orders carry no algorithm version: atlas-algos stamps each manifest with its own
version at compute time, so the release is never pinned at planning time.
"""
import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--end", type=int, required=True)
    ap.add_argument("--shard-size", type=int, required=True)
    ap.add_argument("--columns", required=True, help="comma-separated column names")
    ap.add_argument("--table", default="numbers")
    ap.add_argument("--algorithm-release", default="",
                    help="(optional) hint only; atlas-algos stamps the real version at compute time")
    ap.add_argument("--out", default=str(ROOT / "pending"))
    a = ap.parse_args()

    cols = [c.strip() for c in a.columns.split(",") if c.strip()]
    if not cols:
        raise SystemExit("no columns given")
    os.makedirs(a.out, exist_ok=True)

    n, s = 0, a.start
    while s <= a.end:
        e = min(s + a.shard_size - 1, a.end)
        wid = f"T-{a.table}-{s}-{e}"
        wo = {
            "id": wid,
            "table": a.table,
            "range_start": s,
            "range_end": e,
            "columns": cols,
            "algorithm_release": a.algorithm_release,
            "expected_row_count": e - s + 1,
        }
        with open(os.path.join(a.out, wid + ".json"), "w") as f:
            json.dump(wo, f, indent=2)
            f.write("\n")
        n += 1
        s = e + 1
    print(f"wrote {n} work order(s) to {a.out}")


if __name__ == "__main__":
    main()
