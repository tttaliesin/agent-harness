#!/usr/bin/env python3
"""Render a reviewed tooling specification into a NEW directory; never install tools."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys

TEMPLATE_VERSION = "1.0.0"
KINDS = {"python", "node", "go", "rust", "custom"}
OPERATIONS = {"lint", "format", "test", "build", "dev"}
EXACT = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?\Z")
NAME = re.compile(r"[a-z][a-z0-9-]*\Z")


def quote(value):
    return json.dumps(value, ensure_ascii=False)


def validate(spec):
    if spec.get("schema") != 1:
        raise ValueError("schema must be 1")
    if not EXACT.fullmatch(spec.get("mise_version", "")):
        raise ValueError("mise_version must be an exact version")
    if tuple(map(int, spec["mise_version"].split("-")[0].split("+")[0].split("."))) < (2026, 8, 10):
        raise ValueError("template requires mise >= 2026.8.10; validate older versions separately")
    tools = spec.get("tools", {})
    if not isinstance(tools, dict):
        raise ValueError("tools must be a mapping")
    for name, version in tools.items():
        if not re.fullmatch(r"[A-Za-z0-9_:./-]+", name) or not EXACT.fullmatch(version):
            raise ValueError(f"exact tool version required: {name}")
    if "rust" in tools or "rustup" in tools:
        raise ValueError("Rust uses an environment-provided rustup and rust_toolchain, not mise tools")
    modules = spec.get("modules", [])
    if not modules:
        raise ValueError("at least one module is required")
    names = set()
    for module in modules:
        name, kind = module.get("name", ""), module.get("kind")
        if not NAME.fullmatch(name) or name in names or kind not in KINDS:
            raise ValueError("module names must be unique lowercase slugs; kind must be supported")
        names.add(name)
        path = module.get("path", "")
        pure = PurePosixPath(path)
        if not path or pure.is_absolute() or ".." in pure.parts or "\\" in path or ":" in path:
            raise ValueError(f"module path must stay inside repository: {name}")
        if any(ord(c) < 32 for c in path):
            raise ValueError("control character in module path")
        required = {"python": {"python", "uv"}, "node": {"node", "pnpm"},
                    "go": {"go"}, "rust": set(), "custom": set()}[kind]
        if not required <= tools.keys():
            raise ValueError(f"{name} requires tools {sorted(required)}")
        commands = module.get("commands", {})
        if not commands or set(commands) - OPERATIONS:
            raise ValueError(f"{name} needs supported commands: {sorted(OPERATIONS)}")
        for operation, entries in commands.items():
            if not isinstance(entries, list) or not entries or any(not isinstance(c, str) or not c.strip() for c in entries):
                raise ValueError(f"{name}:{operation} must contain nonempty command strings")
        if not set(commands) & {"lint", "test", "build"}:
            raise ValueError(f"{name} needs at least one real check operation")
    if any(m["kind"] == "rust" for m in modules) and not EXACT.fullmatch(spec.get("rust_toolchain", "")):
        raise ValueError("Rust requires exact rust_toolchain")
    if "pnpm" in tools and int(tools["pnpm"].split(".")[0]) not in {10, 11, 12}:
        raise ValueError("pnpm template supports majors 10–12; review other majors before extending")
    if "pnpm" in tools and tuple(map(int, tools["pnpm"].split("-")[0].split("+")[0].split("."))) < (10, 6, 0):
        raise ValueError("pnpm >= 10.6.0 required for workspace YAML settings")


def render(spec):
    validate(spec)
    tools, modules = spec["tools"], spec["modules"]
    kinds = {m["kind"] for m in modules}
    lines = [f"# development-tooling template {TEMPLATE_VERSION}",
             "# Review before trusting; native commands remain owned by each module.",
             "[tools]"]
    lines.extend(f"{quote(k)} = {quote(v)}" for k, v in sorted(tools.items()))
    lines += ["", "[settings]", "experimental = false", "idiomatic_version_file_enable_tools = []",
              "", "[settings.task]", "run_auto_install = false", "", "[env]"]
    if "python" in kinds:
        lines += ['UV_PYTHON = { value = "{{ tools.python.path }}", tools = true }',
                  'UV_PYTHON_DOWNLOADS = "never"', 'UV_PYTHON_PREFERENCE = "only-system"']
    if "go" in kinds:
        lines += ['GOTOOLCHAIN = "local"']
    if "rust" in kinds:
        lines += ['RUSTUP_AUTO_INSTALL = "0"']

    def task(name, commands, description, directory=None):
        lines.extend(["", f"[tasks.{quote(name)}]", f"description = {quote(description)}"])
        # Make module paths relative to the declaring root even when invoked from a subdirectory.
        if directory is not None:
            lines.append('dir = ' + quote("{{ config_root }}/" + directory))
        lines.append("run = " + quote(commands))

    task("default", ["mise tasks"], "List available development commands", ".")
    task("doctor", ["mise --version"] + ["mise run doctor:" + m["name"] for m in modules],
         "Inspect selected runtimes without installing or repairing", ".")
    grouped = {op: [] for op in ["sync", "lint", "format", "test", "build"]}
    rust_guard = (
        'unset RUSTUP_TOOLCHAIN; tooling_rust_version=$(rustc --version) && '
        'case "$tooling_rust_version" in ' + quote("rustc " + spec.get("rust_toolchain", "") + " ") +
        '*) ;; *) echo "Rust compiler differs from the adopted toolchain; inspect overrides" >&2; exit 1 ;; esac'
    )
    for module in modules:
        name, kind, directory = module["name"], module["kind"], module["path"]
        doctor = {"python": ["python --version", "uv --version", "python -c 'import sys; print(sys.executable)'"],
                  "node": ["node --version", "pnpm --version", "node -p process.execPath"],
                  "go": ["go version", "go env GOTOOLCHAIN GOROOT"],
                  "rust": ["rustup --version", "rustup toolchain list", "rustup show active-toolchain", "rustc --version"],
                  "custom": ["mise --version"]}[kind]
        if kind == "rust":
            doctor = ["unset RUSTUP_TOOLCHAIN; " + command for command in doctor]
            doctor.append(rust_guard)
        task("doctor:" + name, doctor, "Inspect " + name, directory)
        sync = {"python": ["uv sync --locked"], "node": ["pnpm install --frozen-lockfile"],
                "go": ['''tooling_snapshot=$(mktemp -d)
trap 'rm -rf "$tooling_snapshot"' EXIT
cp go.mod "$tooling_snapshot/go.mod"
if [ -f go.sum ]; then cp go.sum "$tooling_snapshot/go.sum"; fi
go mod download
go mod verify
cmp go.mod "$tooling_snapshot/go.mod"
if [ -f "$tooling_snapshot/go.sum" ]; then
  cmp go.sum "$tooling_snapshot/go.sum"
else
  test ! -f go.sum
fi'''],
                "rust": [rust_guard, "unset RUSTUP_TOOLCHAIN; rustup show active-toolchain",
                         "unset RUSTUP_TOOLCHAIN; cargo fetch --locked"], "custom": []}[kind]
        if sync:
            task("sync:" + name, sync, "Synchronize locked dependencies for " + name, directory)
            grouped["sync"].append("mise run sync:" + name)
        for op, commands in sorted(module["commands"].items()):
            if kind == "python":
                # --no-sync implies --frozen: check the lock separately first.
                commands = ["test -x .venv/bin/python",
                            '''tooling_python_version=$(python -c 'import sys; print(sys.version)')
tooling_venv_version=$(.venv/bin/python -c 'import sys; print(sys.version)')
test "$tooling_python_version" = "$tooling_venv_version"''',
                            "uv lock --check"] + [
                    "export UV_NO_SYNC=true; " + command for command in commands]
            if kind == "rust":
                # mise env=false did not remove inherited values in the tested version.
                commands = [rust_guard] + ["unset RUSTUP_TOOLCHAIN; " + command for command in commands]
            task(op + ":" + name, commands, op + " " + name, directory)
            if op in grouped:
                grouped[op].append("mise run " + op + ":" + name)
    for op, commands in grouped.items():
        if commands:
            task(op, commands, op + " all applicable modules in order", ".")
    task("check", ["mise run " + op for op in ["lint", "test", "build"] if grouped[op]],
         "Run declared checks in order; stop on failure; no dependency installation", ".")

    record = {"template": "development-tooling", "template_version": TEMPLATE_VERSION,
              "mise_version": spec["mise_version"], "spec": spec,
              "validation": "pending: generated declarations are not adoption evidence"}
    files = {"mise.toml": "\n".join(lines) + "\n",
             "tooling-template.json": json.dumps(record, ensure_ascii=False, indent=2) + "\n",
             "gitignore.fragment": ".venv/\nnode_modules/\n__pycache__/\n.mise.local.toml\nmise.local.toml\n.env\n.env.*\n!.env.example\n"}
    if "rust" in kinds:
        files["rust-toolchain.toml"] = ('[toolchain]\nchannel = ' + quote(spec["rust_toolchain"]) +
                                         '\nprofile = "minimal"\ncomponents = ["rustfmt", "clippy"]\n')
    if "node" in kinds:
        major = int(tools["pnpm"].split(".")[0])
        files["pnpm-workspace.fragment.yaml"] = (
            "# Merge into each independent pnpm workspace root; do not replace package lists.\n" +
            ("managePackageManagerVersions: false\npackageManagerStrictVersion: true\n" if major == 10 else
             "pmOnFail: error\nruntimeOnFail: error\n"))
        files["package.fragment.json"] = json.dumps({"packageManager": "pnpm@" + tools["pnpm"]}, indent=2) + "\n"
    files["ADOPTION.md"] = """# Tooling adoption record

This output is a tooling overlay, not an application scaffold or a completed migration.
Commands supplied by the specification execute code; review them before trusting mise.toml.

## Apply

1. Compare this overlay with the target repository and merge the selected files.
2. Merge fragments into the real ignore, package and pnpm workspace files; never replace existing content blindly.
3. Provide module manifests, their committed dependency locks and the actual commands named by the specification.
4. Provision the recorded mise version and, for Rust, an environment-owned rustup with its proxy directory on PATH.
5. Review and trust the target mise.toml; explicitly install pinned tools and any selected Rust toolchain.
6. Resolve mise.lock for supported backends and platforms, then verify mise install --locked where covered.
7. Run mise run sync, mise run doctor and mise run check in a clean supported environment.
8. Check runtime paths, lock immutability, failure propagation and representative user behavior.

## Record before accepting

- Purpose and modules
- Supported OS, architecture, image digest and bootstrap artifact verification
- Previous configuration revision and template version
- Compatibility floors versus exact development runtime versions
- Rustup bootstrap version, selected compiler and targets when applicable
- Exact commands and results, including unavailable checks
- Lock coverage, backend exceptions and dependency install script decisions
- Missing operations and their reason; required checks must never be replaced with successful no-ops
- Duplicate selectors and temporary task adapters to remove
- Previous configuration, locks and image needed for rollback

Generation does not install, trust, update locks, execute supplied commands or change any existing project.
"""
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("output", type=Path, help="new directory; refuses every existing path")
    args = parser.parse_args()
    try:
        files = render(json.loads(args.spec.read_text()))
        # Exclusive creation also refuses existing and dangling symlinks.
        args.output.mkdir(parents=False, exist_ok=False)
        for name, content in files.items():
            (args.output / name).write_text(content)
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(1, f"tooling template: {error}\n")
    print(f"Rendered {TEMPLATE_VERSION}: {args.output} ({len(files)} files); adoption pending")


if __name__ == "__main__":
    main()
