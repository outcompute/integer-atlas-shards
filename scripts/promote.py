"""Move every computed/ manifest to accepted/, flipping verification.status.

Runs after a PR merges (promote.yml). Whatever is in computed/ on main has already
passed pr-validate, so promotion is a status flip + move. publish.yml then rebuilds.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPUTED = ROOT / "computed"
ACCEPTED = ROOT / "accepted"


def main():
    moved = 0
    for f in sorted(COMPUTED.rglob("*.json")):
        m = json.loads(f.read_text())
        v = m.setdefault("verification", {})
        v["status"] = "accepted"
        v["verified_at_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        dest = ACCEPTED / f.relative_to(COMPUTED)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(m, indent=2) + "\n")
        f.unlink()
        moved += 1
    print(f"promoted {moved} shard(s)")


if __name__ == "__main__":
    main()
