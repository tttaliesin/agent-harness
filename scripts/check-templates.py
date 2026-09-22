"""Verify role templates and their explicit binding without writing products."""

import hashlib
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"explorer", "spec_reviewer", "standards_reviewer", "domain_reviewer"}


def main():
    manifest = json.loads((ROOT / "templates/binding.json").read_text())
    if (
        manifest["package_digest"]
        != hashlib.sha256((ROOT / "upstream.lock.json").read_bytes()).hexdigest()
    ):
        raise SystemExit("Binding refers to a different shared package lock")
    found = set()
    for entry in manifest["files"]:
        source = ROOT / "templates" / entry["source"]
        if source.resolve().parent != (ROOT / "templates/agents").resolve():
            raise SystemExit("Unexpected template source")
        expected_target = f".codex/agents/{source.name}"
        if entry["target"] != expected_target:
            raise SystemExit("Unexpected product target")
        if hashlib.sha256(source.read_bytes()).hexdigest() != entry["sha256"]:
            raise SystemExit(f"Stale binding hash: {source.name}")
        data = tomllib.loads(source.read_text())
        if data["name"] in found or data["sandbox_mode"] != "read-only" or "model" in data:
            raise SystemExit("Invalid role declaration")
        if not data["description"] or not data["developer_instructions"]:
            raise SystemExit("Missing role instructions")
        found.add(data["name"])
    if found != EXPECTED:
        raise SystemExit("Missing or extra role")
    print("PASS: four role templates and explicit binding hashes")


if __name__ == "__main__":
    main()
