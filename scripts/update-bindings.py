"""Explicitly refresh derived role binding after reviewing the shared package lock."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = {
        "schema_version": 1,
        "package_version": "0.1.0",
        "package_digest": hashlib.sha256((ROOT / "upstream.lock.json").read_bytes()).hexdigest(),
        "files": [
            {
                "source": f"agents/{path.name}",
                "target": f".codex/agents/{path.name}",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in sorted((ROOT / "templates/agents").glob("*.toml"))
        ],
    }
    target = ROOT / "templates/binding.json"
    data = json.dumps(manifest, indent=2) + "\n"
    if target.read_text() != data:
        target.write_text(data, encoding="utf-8", newline="\n")
    print("Binding now references the current shared package lock")


if __name__ == "__main__":
    main()
