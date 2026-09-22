"""Exercise formal review preconditions against a real temporary Git repository."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/code-review/scripts/check-candidate.py"


def git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, encoding="utf-8", stderr=subprocess.PIPE
    ).strip()


@pytest.fixture
def candidate(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.name", "Fixture")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    (tmp_path / "spec.md").write_text("Return a greeting.\n", encoding="utf-8")
    git(tmp_path, "add", "spec.md")
    git(tmp_path, "commit", "-qm", "spec")
    base = git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "app.txt").write_text("hello\n", encoding="utf-8")
    git(tmp_path, "add", "app.txt")
    git(tmp_path, "commit", "-qm", "behavior")
    return tmp_path, base, git(tmp_path, "rev-parse", "HEAD")


def check(candidate, *extra):
    root, base, head = candidate
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(root),
            "--base",
            base,
            "--candidate",
            head,
            "--spec",
            "spec.md",
            *extra,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return result.returncode, json.loads(result.stdout)


def test_clean_candidate_identifies_spec_and_commit(candidate):
    code, report = check(candidate)
    assert code == 0
    assert report["status"] == "READY"
    assert report["candidate"] == candidate[2]
    assert report["specifications"][0]["path"] == "spec.md"
    assert len(report["specifications"][0]["sha256"]) == 64


@pytest.mark.parametrize("state", ["tracked", "untracked", "staged"])
def test_dirty_candidate_cannot_be_formally_accepted(candidate, state):
    root = candidate[0]
    (root / ("app.txt" if state == "tracked" else "new.txt")).write_text("changed\n")
    if state == "staged":
        git(root, "add", "new.txt")
    code, report = check(candidate)
    assert code == 2
    assert report["status"] == "BLOCKED"
    assert "dirty" in report["reason"]


def test_missing_required_spec_blocks(candidate):
    code, report = check(candidate, "--spec", "missing.md")
    assert code == 2
    assert "specification" in report["reason"]


def test_changed_candidate_rejects_stale_request(candidate):
    git(candidate[0], "commit", "--allow-empty", "-qm", "new candidate")
    code, report = check(candidate)
    assert code == 2
    assert "candidate" in report["reason"]


def test_empty_diff_cannot_pass(candidate):
    code, report = check(candidate, "--base", candidate[2])
    assert code == 2
    assert "empty" in report["reason"]


def test_external_spec_is_not_read(candidate):
    code, report = check(candidate, "--spec", "../outside.md")
    assert code == 2
    assert "specification" in report["reason"]


@pytest.mark.parametrize("flag", ["--assume-unchanged", "--skip-worktree"])
def test_hidden_tracked_changes_block_formal_review(candidate, flag):
    root = candidate[0]
    git(root, "update-index", flag, "spec.md")
    (root / "spec.md").write_text("Different acceptance criteria.\n")
    assert not git(root, "status", "--porcelain")
    code, report = check(candidate)
    assert code == 2
    assert "hidden" in report["reason"]
