"""Run an already installed pinned OpenSpec CLI with an isolated custom profile."""

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", type=Path, required=True)
    parser.add_argument("--node", required=True)
    parser.add_argument("--cli", type=Path, required=True, help="Installed bin/openspec.js")
    args = parser.parse_args()
    profile = json.loads((ROOT / "openspec-profile.json").read_text())
    cli = args.cli.resolve(strict=True)
    product = args.product.resolve(strict=True)
    if not product.is_dir():
        raise SystemExit("Product root must be a directory")
    command = [args.node, str(cli)]
    env = dict(os.environ, OPENSPEC_TELEMETRY="0", DO_NOT_TRACK="1")
    version = subprocess.check_output(command + ["--version"], env=env, text=True).strip()
    if version != profile["version"]:
        raise SystemExit(f"Expected OpenSpec {profile['version']}; observed {version}")
    # The installed package must match the lock; this script never downloads a CLI.
    package = json.loads((cli.parent.parent / "package.json").read_text())
    if package["name"] != profile["package"] or package["version"] != profile["version"]:
        raise SystemExit("Installed package identity mismatch")
    with tempfile.TemporaryDirectory(prefix="harness-openspec-") as temporary:
        env["XDG_CONFIG_HOME"] = temporary
        env["XDG_DATA_HOME"] = temporary
        for key, value in (
            ("profile", profile["profile"]),
            ("workflows", json.dumps(profile["workflows"])),
        ):
            subprocess.run(command + ["config", "set", key, value], env=env, check=True)
        subprocess.run(
            command
            + [
                "init",
                str(product),
                "--tools",
                "codex",
                "--profile",
                "custom",
                "--no-animation",
                "--no-copilot-cloud",
            ],
            cwd=product,
            env=env,
            check=True,
        )
    generated = {
        path.parent.name for path in (product / ".agents/skills").glob("openspec-*/SKILL.md")
    }
    if generated != set(profile["skills"]):
        raise SystemExit(f"Unexpected generated skills: {sorted(generated)}")
    print(json.dumps({"status": "PASS", "version": version, "skills": sorted(generated)}))


if __name__ == "__main__":
    main()
