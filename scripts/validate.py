"""Validate manifests (computed/, accepted/) and work orders (pending/) against the
JSON schemas, plus basic range sanity. Exits non-zero on any problem.
"""
import glob
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent.parent


def _load(p):
    return json.loads(Path(p).read_text())


def main():
    manifest_schema = _load(ROOT / "schema/manifest.schema.json")
    wo_schema = _load(ROOT / "schema/work-order.schema.json")
    errors = []

    for f in glob.glob(str(ROOT / "computed/**/*.json"), recursive=True) + \
             glob.glob(str(ROOT / "accepted/**/*.json"), recursive=True):
        m = _load(f)
        try:
            jsonschema.validate(m, manifest_schema)
        except jsonschema.ValidationError as e:
            errors.append(f"{f}: {e.message}")
            continue
        if m["range_start"] > m["range_end"]:
            errors.append(f"{f}: range_start > range_end")
        if m["row_count"] > m["range_end"] - m["range_start"] + 1:
            errors.append(f"{f}: row_count exceeds the range")

    for f in glob.glob(str(ROOT / "pending/**/*.json"), recursive=True):
        try:
            jsonschema.validate(_load(f), wo_schema)
        except jsonschema.ValidationError as e:
            errors.append(f"{f}: {e.message}")

    if errors:
        print("INVALID:\n" + "\n".join(errors))
        sys.exit(1)
    print("all manifests and work orders valid")


if __name__ == "__main__":
    main()
