"""Native Git inspection; no git state mutation and no environment-selected checkout."""

import hashlib
import os
import re
import subprocess
from pathlib import Path

from .common import HarnessError, blocked, digest, safe_path
from .process import executable


class Git:
    def __init__(self, root, binary="git"):
        self.root = Path(root).resolve(strict=True)
        self.binary = executable([binary])
        top = Path(self.call("rev-parse", "--show-toplevel").strip()).resolve()
        if top != self.root:
            raise HarnessError("root_must_be_git_toplevel")

    def call(self, *args, allow_failure=False):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env["GIT_TERMINAL_PROMPT"] = "0"
        try:
            completed = subprocess.run(
                [
                    self.binary,
                    "--no-optional-locks",
                    "-c",
                    "core.fsmonitor=false",
                    "-c",
                    "core.untrackedCache=false",
                    "-C",
                    str(self.root),
                    *args,
                ],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                timeout=15,
                env=env,
                shell=False,
                encoding="utf-8",
                errors="strict",
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            blocked("git_unavailable", detail=str(exc))
        if completed.returncode and not allow_failure:
            raise HarnessError("git_failed", command=list(args), detail=completed.stderr.strip())
        return completed.stdout

    def commit(self, value):
        # Require immutable input; reject options, branch races and revision expression injection.
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
            raise HarnessError("commit_sha_required", value=value)
        return self.call("rev-parse", "--verify", f"{value}^{{commit}}").strip()

    def snapshot(self, base):
        base = self.commit(base)
        head = self.call("rev-parse", "HEAD").strip()
        return {
            "head": head,
            "base": base,
            "tree": self.call("rev-parse", "HEAD^{tree}").strip(),
            "dirty": bool(self.call("status", "--porcelain=v1", "--untracked-files=all")),
            "worktree": self.worktree_digest(),
        }

    def worktree_digest(self):
        files = {}
        names = self.call("ls-files", "-z", "--cached", "--others", "--exclude-standard")
        for name in sorted(set(names.split("\0")) - {""}):
            path = safe_path(self.root, name)
            if not path.exists():
                files[name] = None
            elif path.is_file():
                with path.open("rb") as stream:
                    files[name] = hashlib.file_digest(stream, "sha256").hexdigest()
            else:
                blocked("unsupported_git_input", path=name)
        return digest(files)

    def require_clean(self):
        entries = self.call("ls-files", "-v", "-z").split("\0")
        if any(entry and (entry[0].islower() or entry[0] == "S") for entry in entries):
            blocked("hidden_index_flags")
        if self.call("status", "--porcelain=v1", "--untracked-files=all"):
            blocked("dirty_tree")

    def ignored_outputs(self):
        if not self.call("check-ignore", ".harness/probe", allow_failure=True).strip():
            blocked("harness_outputs_must_be_gitignored")

    def base_file(self, base, path):
        return self.call("show", f"{self.commit(base)}:{path}")

    def changed(self, base):
        return [
            p
            for p in self.call(
                "diff", "--name-only", "-z", "--no-renames", self.commit(base), "HEAD", "--"
            ).split("\0")
            if p
        ]
