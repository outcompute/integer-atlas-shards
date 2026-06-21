"""Verify submitted shards in computed/ before merge.

For each manifest in computed/: download the shard from its storage URL, check the
SHA-256, and run `atlas-algos verify` to the given degree. Exits non-zero on any
failure. Requires `atlas-algos` on PATH (CI installs integer-atlas-algos).
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest):
    if url.startswith("file://"):
        shutil.copyfile(url[len("file://"):], dest)
    elif "://" not in url:
        shutil.copyfile(url, dest)
    else:
        urllib.request.urlretrieve(url, dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--degree", type=float, default=0.1)
    args = ap.parse_args()

    manifests = sorted((ROOT / "computed").rglob("*.json"))
    if not manifests:
        print("no computed/ manifests to verify")
        return 0

    failures = 0
    for mp in manifests:
        m = json.loads(mp.read_text())
        urls = m.get("storage") or []
        if not urls:
            print(f"FAIL {mp.name}: no storage URL")
            failures += 1
            continue
        with tempfile.TemporaryDirectory() as td:
            shard = str(Path(td) / m["file"])
            try:
                download(urls[0], shard)
            except Exception as e:
                print(f"FAIL {mp.name}: download failed: {e}")
                failures += 1
                continue
            want = m.get("hashes", {}).get("sha256")
            if want and sha256(shard) != want:
                print(f"FAIL {mp.name}: sha256 mismatch")
                failures += 1
                continue
            r = subprocess.run(["atlas-algos", "verify", "--manifest", str(mp),
                                "--shard", shard, "--degree", str(args.degree)])
            if r.returncode != 0:
                print(f"FAIL {mp.name}: recompute mismatch (exit {r.returncode})")
                failures += 1
                continue
        print(f"ok   {mp.name}")

    if failures:
        print(f"{failures} failure(s)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
