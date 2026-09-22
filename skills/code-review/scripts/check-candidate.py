"""Read-only preflight for a formal review; never runs checks or creates evidence."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


class Blocked(ValueError):
    """A formal review prerequisite is unavailable."""


def git(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    if result.returncode:
        raise Blocked("Git inspection failed; check repository, references and access")
    return result.stdout.strip()


def inspect(args):
    root = args.repo.resolve(strict=True)
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise Blocked("repo must be the actual Git root")
    if not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", args.candidate):
        raise Blocked("candidate must be a full commit SHA")
    head = git(root, "rev-parse", "HEAD")
    if head != args.candidate.lower():
        raise Blocked("candidate changed since the review request")
    # Status deliberately omits these entries; do not clear user index flags.
    if any(
        row and (row[0].islower() or row[0] == "S")
        for row in git(root, "ls-files", "-v", "-z").split("\0")
    ):
        raise Blocked("hidden tracked changes possible: assume-unchanged or skip-worktree")
    if git(root, "status", "--porcelain", "--untracked-files=all"):
        raise Blocked("dirty candidate; record a WIP review or commit the authorized work first")
    base = git(root, "rev-parse", "--verify", "--end-of-options", args.base + "^{commit}")
    merge_base = git(root, "merge-base", base, head)
    changed = git(root, "diff", "--name-only", merge_base, head, "--")
    if not changed:
        raise Blocked("empty comparison; no candidate change to review")
    specifications = []
    for value in args.spec:
        path = (root / value).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise Blocked("required specification missing or outside repository")
        relative = path.relative_to(root).as_posix()
        git(root, "ls-files", "--error-unmatch", "--", relative)
        data = path.read_bytes()
        if not data.strip():
            raise Blocked("required specification is empty")
        specifications.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest()})
    if git(root, "rev-parse", "HEAD") != head or git(
        root, "status", "--porcelain", "--untracked-files=all"
    ):
        raise Blocked("candidate changed during inspection")
    return {
        "status": "READY",
        "base": base,
        "merge_base": merge_base,
        "candidate": head,
        "specifications": specifications,
        "changed_files": changed.splitlines(),
        "product_checks_verified": False,
        "review_permissions_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--base", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--spec", required=True, action="append")
    args = parser.parse_args()
    try:
        result = inspect(args)
    except (Blocked, OSError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}))
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
