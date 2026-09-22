#!/usr/bin/env python3
"""Verify the selected Codex packages offline, without updating the lock.

The lock is reviewed input, not a signature. Git object proofs bind vendored
bytes to a commit; they cannot authenticate a remote repository without an
independently trusted pin. No Git executable or network is used here.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    yaml = None

MATT_NAMES = {"domain-modeling", "grilling", "codebase-design", "code-review"}
SUPERPOWERS_NAMES = {"test-driven-development", "verification-before-completion"}
SOURCES = {
    "mattpocock-skills": "https://github.com/mattpocock/skills",
    "superpowers": "https://github.com/obra/superpowers",
    "superpowers-debugging": "https://github.com/obra/superpowers",
}
MERGED_SOURCES = {
    "mattpocock-skills": {
        "skills/engineering/grill-with-docs/SKILL.md": (
            "skills/grilling/references/record-decisions.md"
        ),
        "skills/productivity/writing-for-agents/SKILL.md": (
            "skills/markdown-authoring/references/writing-for-agents.md"
        ),
    },
    "superpowers": {
        "skills/receiving-code-review/SKILL.md": (
            "skills/code-review/references/receiving-review.md"
        ),
    },
}
LICENSE_COPIES = {
    **{f"skills/{name}/LICENSE.txt": "mattpocock-skills" for name in MATT_NAMES},
    **{f"skills/{name}/LICENSE.txt": "superpowers" for name in SUPERPOWERS_NAMES},
    "skills/markdown-authoring/LICENSE.mattpocock.txt": "mattpocock-skills",
    "skills/code-review/LICENSE.superpowers.txt": "superpowers",
}
PACKAGE_DIRS = ("skills", "provenance", "docs", "scripts", "tests", "plugins")
EXTRA_FILES = (
    "THIRD_PARTY_NOTICES.md",
    "pyproject.toml",
    "uv.lock",
    "mise.toml",
    "mise.lock",
    "justfile",
    ".github/workflows/check.yml",
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "README.md",
)
IGNORED_DIRS = {"__pycache__", "node_modules", ".git", ".pytest_cache", ".venv"}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
RESERVED = re.compile(r"(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?\Z", re.IGNORECASE)


class PackageError(ValueError):
    """Invalid or incomplete packaging evidence."""


def require(condition, message):
    if not condition:
        raise PackageError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def keys(value, required, optional=(), label="record"):
    require(isinstance(value, dict), f"{label}: expected object")
    require(
        set(required) <= value.keys(),
        f"{label}: missing fields {set(required) - value.keys()}",
    )
    require(
        value.keys() <= set(required) | set(optional),
        f"{label}: unknown fields {value.keys() - set(required) - set(optional)}",
    )


def nonempty(value, label):
    require(
        isinstance(value, str) and bool(value.strip()),
        f"{label}: expected nonempty string",
    )


def canonical_path(raw):
    nonempty(raw, "path")
    require(
        "\\" not in raw and ":" not in raw and not raw.startswith("/"),
        f"unsafe path: {raw}",
    )
    parts = raw.split("/")
    require(
        all(
            p
            and p not in (".", "..")
            and not p.endswith((".", " "))
            and not RESERVED.fullmatch(p)
            and not any(ord(c) < 32 for c in p)
            and not any(c in p for c in '<>"|?*')
            for p in parts
        ),
        f"unsafe path: {raw}",
    )
    return parts


def safe_path(root, raw, *, exists=True):
    path = root
    for part in canonical_path(raw):
        path = path / part
        try:
            info = path.lstat()
        except FileNotFoundError:
            require(not exists, f"missing file or directory: {raw}")
            continue
        require(
            not stat.S_ISLNK(info.st_mode) and not (getattr(info, "st_file_attributes", 0) & 0x400),
            f"symlink/reparse path rejected: {raw}",
        )
    require(path.resolve().is_relative_to(root), f"path escapes root: {raw}")
    return path


def checked_root(root):
    root = Path(root).absolute()
    require(root.is_dir(), f"missing root: {root}")
    for path in (root, *root.parents):
        info = path.lstat()
        require(
            not stat.S_ISLNK(info.st_mode) and not (getattr(info, "st_file_attributes", 0) & 0x400),
            f"symlink/reparse root rejected: {root}",
        )
    return root.resolve()


def read(root, raw):
    path = safe_path(root, raw)
    require(path.is_file(), f"expected regular file: {raw}")
    require(stat.S_ISREG(path.stat().st_mode), f"special file rejected: {raw}")
    return path.read_bytes()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(data):
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique_object)


def inventory(root):
    """Exact managed file set; ignored runtime caches are never artifacts."""
    result = {}
    folded = {}
    for directory in PACKAGE_DIRS:
        base = safe_path(root, directory, exists=False)
        if not base.exists():
            continue
        require(base.is_dir(), f"expected package directory: {directory}")
        for parent, dirs, files in os.walk(base, followlinks=False):
            # Check even ignored entries for reparse points before pruning them.
            for name in dirs + files:
                relative = (Path(parent) / name).relative_to(root).as_posix()
                safe_path(root, relative)
                require(
                    relative.casefold() not in folded,
                    f"case-colliding path: {relative}",
                )
                folded[relative.casefold()] = relative
            dirs[:] = sorted(
                d for d in dirs if d not in IGNORED_DIRS and not d.endswith(".egg-info")
            )
            for name in sorted(files):
                if name.endswith((".pyc", ".pyo")):
                    continue
                relative = (Path(parent) / name).relative_to(root).as_posix()
                if relative == "templates/binding.json":
                    # Derived from this lock; verified separately to avoid a hash cycle.
                    continue
                result[relative] = sha256(read(root, relative))
    for relative in EXTRA_FILES:
        result[relative] = sha256(read(root, relative))
    require(result, "empty artifact inventory")
    return dict(sorted(result.items()))


def git_oid(kind, data):
    # Git SHA-1 is the upstream object format, not our artifact digest algorithm.
    return hashlib.sha1(f"{kind} {len(data)}\0".encode() + data).hexdigest()


def tree_entries(data):
    entries = {}
    cursor = 0
    while cursor < len(data):
        space = data.index(b" ", cursor)
        end = data.index(b"\0", space)
        mode = data[cursor:space].decode("ascii")
        name = data[space + 1 : end].decode("utf-8")
        require(len(data[end + 1 : end + 21]) == 20, "truncated Git tree")
        canonical_path(name)
        require("/" not in name and name not in entries, "invalid Git tree entry")
        entries[name] = (mode, data[end + 1 : end + 21].hex())
        cursor = end + 21
    return entries


def prefix_for(source):
    return f"provenance/{source['id']}"


def target_for(source_id, upstream):
    parts = canonical_path(upstream)
    if upstream == "LICENSE":
        return f"provenance/{source_id}/LICENSE.txt"
    if upstream in MERGED_SOURCES.get(source_id, {}):
        return MERGED_SOURCES[source_id][upstream]
    if source_id == "mattpocock-skills":
        require(
            len(parts) >= 4 and parts[0] == "skills" and parts[2] in MATT_NAMES,
            f"unselected Matt path: {upstream}",
        )
        category = "productivity" if parts[2] == "grilling" else "engineering"
        require(parts[1] == category, f"incorrect upstream category: {upstream}")
        return "skills/" + "/".join(parts[2:])
    names = SUPERPOWERS_NAMES if source_id == "superpowers" else {"systematic-debugging"}
    require(
        len(parts) >= 3 and parts[0] == "skills" and parts[1] in names,
        f"unselected Superpowers path: {upstream}",
    )
    return upstream


def validate_sources(root, sources, artifacts):
    require(isinstance(sources, list), "sources must be a list")
    ids = [s.get("id") if isinstance(s, dict) else None for s in sources]
    require(
        len(ids) == len(SOURCES) and set(ids) == set(SOURCES),
        "missing, duplicate, or unknown source IDs",
    )
    all_targets = set()
    for source in sources:
        keys(
            source,
            {"id", "repository", "commit", "license", "selected_paths", "patches"},
            label="source",
        )
        sid = source["id"]
        require(source["repository"] == SOURCES[sid], f"{sid}: unexpected repository")
        require(
            isinstance(source["commit"], str) and HEX40.fullmatch(source["commit"]),
            f"{sid}: commit must be a 40-hex pin",
        )
        prefix = prefix_for(source)
        commit = read(root, f"{prefix}/commit.raw")
        require(
            git_oid("commit", commit) == source["commit"],
            f"{sid}: commit proof mismatch",
        )
        match = re.match(rb"tree ([0-9a-f]{40})\n", commit)
        require(match is not None, f"{sid}: invalid Git commit tree")
        root_tree = match[1].decode()
        selected = source["selected_paths"]
        require(
            isinstance(selected, list) and selected and all(isinstance(p, str) for p in selected),
            f"{sid}: invalid selected_paths",
        )
        require(len(set(selected)) == len(selected), f"{sid}: duplicate selected_paths")
        require("LICENSE" in selected, f"{sid}: missing selected license")
        patches = source["patches"]
        require(
            isinstance(patches, list) and all(isinstance(p, dict) for p in patches),
            f"{sid}: invalid patches",
        )
        require(
            len(patches) == len(selected)
            and {p.get("upstream_path") for p in patches} == set(selected),
            f"{sid}: patch coverage mismatch",
        )
        expected_names = (
            MATT_NAMES
            if sid == "mattpocock-skills"
            else SUPERPOWERS_NAMES
            if sid == "superpowers"
            else {"systematic-debugging"}
        )
        expected_names = expected_names | {p.split("/")[-2] for p in MERGED_SOURCES.get(sid, {})}
        found_names = {p.split("/")[-2] for p in selected if p.endswith("/SKILL.md")}
        require(
            found_names == expected_names,
            f"{sid}: required skill selection is incomplete",
        )
        for patch in patches:
            keys(
                patch,
                {"upstream_path", "target", "upstream_sha256", "sha256", "reason"},
                {"patch", "patch_sha256"},
                label=f"{sid} patch",
            )
            upstream = patch["upstream_path"]
            expected_target = target_for(sid, upstream)
            require(
                patch["target"] == expected_target,
                f"{sid}: invalid target mapping: {upstream}",
            )
            require(
                expected_target not in all_targets,
                f"duplicate source target: {expected_target}",
            )
            all_targets.add(expected_target)
            nonempty(patch["reason"], f"{sid}: patch explanation")
            original = read(root, f"{prefix}/files/{upstream}.source")
            require(
                sha256(original) == patch["upstream_sha256"],
                f"upstream hash mismatch: {upstream}",
            )
            # Walk the captured Git trees to bind the original bytes to the pin.
            tree = root_tree
            parts = upstream.split("/")
            for index, part in enumerate(parts):
                raw_tree = read(root, f"{prefix}/trees/{tree}.raw")
                require(git_oid("tree", raw_tree) == tree, f"{sid}: tree proof mismatch")
                entries = tree_entries(raw_tree)
                require(
                    part in entries,
                    f"{sid}: upstream path absent from commit: {upstream}",
                )
                mode, oid = entries[part]
                if index < len(parts) - 1:
                    require(mode == "40000", f"{sid}: upstream directory is not a tree")
                    tree = oid
                else:
                    require(
                        mode in {"100644", "100755"},
                        f"{sid}: upstream symlink or non-file rejected",
                    )
                    require(
                        git_oid("blob", original) == oid,
                        f"{sid}: blob proof mismatch: {upstream}",
                    )
            actual = read(root, expected_target)
            require(
                sha256(actual) == patch["sha256"],
                f"adapted hash mismatch: {expected_target}",
            )
            require(
                expected_target in artifacts,
                f"source target not covered by artifacts: {expected_target}",
            )
            if actual != original:
                require(
                    set(patch) >= {"patch", "patch_sha256"},
                    f"missing adaptation patch: {expected_target}",
                )
                expected_patch = f"{prefix}/patches/{upstream}.patch"
                require(
                    patch["patch"] == expected_patch,
                    f"invalid patch path: {expected_target}",
                )
                delta = read(root, expected_patch)
                require(
                    sha256(delta) == patch["patch_sha256"],
                    f"patch hash mismatch: {expected_target}",
                )
                expected = "".join(
                    difflib.unified_diff(
                        original.decode().splitlines(keepends=True),
                        actual.decode().splitlines(keepends=True),
                        fromfile=upstream,
                        tofile=expected_target,
                    )
                ).encode()
                require(delta == expected, f"patch content mismatch: {expected_target}")
            else:
                require(
                    "patch" not in patch and "patch_sha256" not in patch,
                    f"redundant adaptation patch: {expected_target}",
                )
        license_info = source["license"]
        keys(license_info, {"spdx", "path", "sha256"}, label=f"{sid} license")
        require(license_info["spdx"] == "MIT", f"{sid}: incorrect license identifier")
        require(
            license_info["path"] == target_for(sid, "LICENSE"),
            f"{sid}: incorrect license path",
        )
        license_bytes = read(root, license_info["path"])
        original_license = read(root, f"{prefix}/files/LICENSE.source")
        require(
            license_bytes == original_license and sha256(license_bytes) == license_info["sha256"],
            f"{sid}: license integrity mismatch",
        )
        require(
            b"MIT License" in license_bytes
            and b"Permission is hereby granted" in license_bytes
            and b"Copyright" in license_bytes,
            f"{sid}: incomplete license",
        )
        notices = read(root, "THIRD_PARTY_NOTICES.md").decode()
        require(
            source["repository"] in notices
            and source["commit"] in notices
            and license_info["path"] in notices,
            f"{sid}: missing third-party notice",
        )
    # A selected skill must carry its license when installed on its own.
    for relative, sid in LICENSE_COPIES.items():
        require(
            read(root, relative) == read(root, f"provenance/{sid}/LICENSE.txt"),
            f"standalone skill license mismatch: {relative}",
        )
    for name in MATT_NAMES | SUPERPOWERS_NAMES:
        for relative in artifacts:
            if relative.startswith(f"skills/{name}/"):
                require(
                    relative in all_targets or relative in LICENSE_COPIES,
                    f"skill file has no upstream correspondence: {relative}",
                )


def yaml_object(text, label):
    require(yaml is not None, "PyYAML is required for offline metadata validation")

    class UniqueLoader(yaml.SafeLoader):
        pass

    def mapping(loader, node):
        loader.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node)
            require(
                isinstance(key, str) and key not in result,
                f"{label}: duplicate/non-string YAML key",
            )
            result[key] = loader.construct_object(value_node)
        return result

    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    value = yaml.load(text, Loader=UniqueLoader)
    require(isinstance(value, dict), f"{label}: expected YAML object")
    return value


def validate_active_skills(root, artifacts):
    names = {}
    entries = []
    for relative in artifacts:
        parts = PurePosixPath(relative).parts
        active = parts[0] == "skills" or (
            len(parts) >= 4 and parts[0] == "plugins" and parts[2] == "skills"
        )
        if not active or parts[-1] != "SKILL.md":
            continue
        contents = read(root, relative).decode("utf-8-sig").replace("\r\n", "\n")
        match = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", contents, re.DOTALL)
        require(match is not None, f"{relative}: missing skill front matter")
        front = yaml_object(match[1], relative)
        name = front.get("name")
        require(
            isinstance(name, str) and NAME.fullmatch(name),
            f"{relative}: invalid skill name",
        )
        require(name == parts[-2], f"{relative}: skill name must match folder")
        nonempty(front.get("description"), f"{relative}: description")
        require(
            name.casefold() not in names,
            f"duplicate active skill name: {name} ({names.get(name.casefold())}, {relative})",
        )
        require(
            front.get("disable-model-invocation", False) is False
            and front.get("disable_model_invocation", False) is False,
            f"{relative}: unsupported disable-model-invocation",
        )
        names[name.casefold()] = relative
        entries.append(relative)
    expected = {
        name: f"skills/{name}/SKILL.md"
        for name in MATT_NAMES | SUPERPOWERS_NAMES | {"systematic-debugging"}
    }
    for name, path in expected.items():
        require(
            names.get(name) == path,
            f"required active skill missing or relocated: {name}",
        )
    return entries


def markdown_body(text):
    """Remove fenced/indented examples; preserve inline link labels and code."""
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            lines.append("")
        elif fence is None:
            lines.append(line)
    require(fence is None, "unclosed Markdown fence")
    return "\n".join(lines)


def markdown_destinations(text):
    body = markdown_body(text)
    definitions = {}
    for match in re.finditer(r"^\s{0,3}\[([^\]]+)\]:\s*(<[^>]+>|\S+)", body, re.MULTILINE):
        definitions[match[1].casefold()] = match[2].strip("<>")
    # Inline links, including nested parentheses in a destination.
    for match in re.finditer(r"\[[^\]\n]+\]\(", body):
        start = match.end()
        depth = 1
        end = start
        angle = start < len(body) and body[start] == "<"
        if angle:
            closing = body.find(">", start + 1)
            require(closing >= 0, "malformed Markdown destination")
            yield body[start + 1 : closing]
            continue
        while end < len(body) and depth:
            if body[end] == "\\":
                end += 2
                continue
            if body[end] == "(":
                depth += 1
            elif body[end] == ")":
                depth -= 1
            end += 1
        require(depth == 0, "malformed Markdown link")
        destination = (
            body[start : end - 1].strip().split(maxsplit=1)[0]
            if body[start : end - 1].strip()
            else ""
        )
        yield destination
    for match in re.finditer(r"\[([^\]\n]+)\]\[([^\]\n]*)\]", body):
        key = (match[2] or match[1]).casefold()
        require(key in definitions, f"undefined Markdown reference: {key}")
        yield definitions[key]
    # Defined shortcut references are required; arbitrary [prose] is not a link.
    for match in re.finditer(r"\[([^\]\n]+)\](?![\[(\:])", body):
        if match[1].casefold() in definitions:
            yield definitions[match[1].casefold()]
    yield from definitions.values()


def resolve_link(root, source, raw):
    if not raw or raw.startswith("#"):
        return None
    parts = urlsplit(raw)
    if parts.scheme in {"https", "http", "mailto"}:
        return None
    require(not parts.scheme and not parts.netloc, f"{source}: unsafe reference {raw}")
    path = unquote(parts.path)
    if not path:
        return None
    require(
        not path.startswith("/") and "\\" not in path and ":" not in path,
        f"{source}: unsafe reference {raw}",
    )
    components = list(PurePosixPath(source).parent.parts)
    for part in path.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            require(components, f"{source}: reference escapes root: {raw}")
            components.pop()
        else:
            components.append(part)
    relative = "/".join(components)
    safe_path(root, relative)
    return relative


def validate_references(root, artifacts, entries):
    # Maintained entrypoints and recursively required references; inert provenance is not guidance.
    pending = set(entries)
    pending.update(p for p in artifacts if p.endswith(".md") and p.startswith("docs/"))
    pending.update({"THIRD_PARTY_NOTICES.md", "README.md", "AGENTS.md"})
    visited = set()
    while pending:
        relative = pending.pop()
        if relative in visited:
            continue
        visited.add(relative)
        for dest in markdown_destinations(read(root, relative).decode("utf-8-sig")):
            target = resolve_link(root, relative, dest)
            if target is not None:
                require(
                    target in artifacts or safe_path(root, target).is_dir(),
                    f"{relative}: required reference is not locked: {target}",
                )
                if target.endswith(".md"):
                    pending.add(target)
    return len(visited)


def verify(root, lock=None):
    """Return deterministic diagnostics; all reads remain within the root."""
    root = checked_root(root)
    if lock is None:
        lock = load_json(read(root, "upstream.lock.json"))
    keys(lock, {"schema_version", "sources", "artifacts"}, label="lock")
    require(
        type(lock["schema_version"]) is int and lock["schema_version"] == 2,
        "unsupported lock schema_version",
    )
    artifacts = lock["artifacts"]
    require(isinstance(artifacts, dict) and artifacts, "missing artifact hashes")
    for path, digest in artifacts.items():
        canonical_path(path)
        require(
            isinstance(digest, str) and HEX64.fullmatch(digest),
            f"invalid artifact SHA-256: {path}",
        )
    current = inventory(root)
    missing = sorted(set(artifacts) - set(current))
    extra = sorted(set(current) - set(artifacts))
    require(not missing, f"missing artifacts: {missing}")
    require(not extra, f"unlocked artifacts: {extra}")
    changed = [path for path in artifacts if current[path] != artifacts[path]]
    require(not changed, f"artifact hash mismatch: {changed}")
    entries = validate_active_skills(root, current)
    require(not any(p.startswith("plugins/") for p in current), "legacy plugin supply remains")
    validate_sources(root, lock["sources"], current)
    references = validate_references(root, current, entries)
    return {
        "status": "PASS",
        "layout": "skills",
        "artifacts": len(current),
        "active_skills": len(entries),
        "markdown_files": references,
        "native_installation_validated": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    if yaml is None:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "errors": ["PyYAML is required; use the project locked environment."],
                }
            )
        )
        return 2
    try:
        report = verify(args.root)
    except (
        PackageError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
        UnicodeError,
        yaml.YAMLError,
    ) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, ensure_ascii=True))
        return 1
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
