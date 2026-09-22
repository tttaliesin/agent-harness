#!/usr/bin/env python3
"""Explicitly rebuild only artifact hashes, preserving all reviewed source pins.

Dry run is the default. --write validates the candidate before atomic replacement.
Changed upstream/adapted bytes, licenses, or provenance need a reviewed source
record and patch update first; this command will not silently bless them.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location(
    "package_checks", Path(__file__).with_name("check-packages.py")
)
checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checks)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--write",
        action="store_true",
        help="Replace the lock after validation; otherwise report the proposed changes only.",
    )
    args = parser.parse_args(argv)
    if checks.yaml is None:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "errors": ["PyYAML is required; use the project locked environment."],
                }
            )
        )
        return 2
    temporary = None
    try:
        root = checks.checked_root(args.root)
        lock_path = checks.safe_path(root, "upstream.lock.json")
        before = lock_path.read_bytes()
        lock = checks.load_json(before)
        checks.keys(lock, {"schema_version", "sources", "artifacts"}, label="lock")
        checks.require(isinstance(lock["artifacts"], dict), "artifacts must be an object")
        previous = lock["artifacts"]
        lock["artifacts"] = checks.inventory(root)
        report = checks.verify(root, lock)
        report.update(
            written=False,
            added=sorted(set(lock["artifacts"]) - set(previous)),
            removed=sorted(set(previous) - set(lock["artifacts"])),
            changed=sorted(
                p
                for p in previous.keys() & lock["artifacts"].keys()
                if previous[p] != lock["artifacts"][p]
            ),
        )
        if args.write:
            checks.require(
                lock_path.read_bytes() == before,
                "lock changed during refresh; retry after review",
            )
            data = (json.dumps(lock, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
            fd, temporary = tempfile.mkstemp(prefix=".package-lock-", suffix=".tmp", dir=root)
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            checks.safe_path(root, "upstream.lock.json")
            # Confirm the package bytes have not changed while building the lock.
            checks.require(
                checks.inventory(root) == lock["artifacts"],
                "artifacts changed during refresh; retry after review",
            )
            checks.require(
                lock_path.read_bytes() == before,
                "lock changed during refresh; retry after review",
            )
            os.replace(temporary, lock_path)
            temporary = None
            report["written"] = True
        print(json.dumps(report))
        return 0
    except (
        checks.PackageError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
        UnicodeError,
        checks.yaml.YAMLError,
    ) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, ensure_ascii=True))
        return 1
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
