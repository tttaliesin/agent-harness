"""Behavioral contracts using real processes and isolated native Git repositories."""

import copy
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from harnesskit import binding, config, evidence, followup, handoff, hooks, review, verification
from harnesskit import workspace as leases
from harnesskit.common import HarnessError, digest, read_json, safe_path, write_json
from harnesskit.git import Git
from harnesskit.process import run
from harnesskit.reports import parse
from harnesskit.schema import SCHEMAS, validate

GIT = os.environ.get("HARNESS_TEST_GIT") or shutil.which("git")
REPO = Path(__file__).resolve().parents[1]
XML = '<testsuite tests="1" failures="0" errors="0" skipped="0"><testcase name="real"/></testsuite>'


def git_command(root, *args):
    assert GIT, "Set HARNESS_TEST_GIT to the native Git executable"
    result = subprocess.run(
        [GIT, "-C", str(root), *args], capture_output=True, text=True, timeout=20, check=True
    )
    return result.stdout.strip()


def commit(root, message="fixture"):
    git_command(root, "add", "--", ".")
    git_command(
        root,
        "-c",
        "user.name=Harness test",
        "-c",
        "user.email=harness@example.invalid",
        "commit",
        "-m",
        message,
    )
    return git_command(root, "rev-parse", "HEAD")


def save_product(root, data):
    (root / "harness/project.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")


def product_fixture(root, body=None):
    root.mkdir(parents=True)
    git_command(root, "init", "-b", "main")
    (root / ".gitignore").write_text(".harness/\n", encoding="utf-8")
    documents = {
        "agents": "AGENTS.md",
        "domain": "CONTEXT.md",
        "architecture": "docs/architecture",
        "decisions": "docs/adr",
        "tracker": "docs/agents/tracker.md",
        "specs": "openspec",
    }
    for path in (
        "AGENTS.md",
        "CONTEXT.md",
        "docs/architecture/overview.md",
        "docs/adr/001.md",
        "docs/agents/tracker.md",
        "openspec/changes/a/proposal.md",
        "openspec/changes/a/specs/requirements.md",
        "src/app.py",
    ):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fixture content\n", encoding="utf-8")
    (root / "harness").mkdir()
    code = body or (
        "import os,pathlib; p=pathlib.Path(os.environ['HARNESS_RUN_DIR'])/'reports/unit.xml';"
        f"p.parent.mkdir(parents=True);p.write_text({XML!r},encoding='utf-8');print('executed')"
    )
    product = {
        "schema_version": 1,
        "project": {"id": "fixture", "root": ".", "packs": ["python"]},
        "documents": documents,
        "verification": {
            "baseline_checks": ["unit"],
            "checks": {
                "unit": {
                    "command": [sys.executable, "-c", code],
                    "kind": "tests",
                    "timeout_seconds": 10,
                    "report": ".harness/runs/{run_id}/reports/unit.xml",
                    "report_format": "junit",
                    "minimum_tests": 1,
                }
            },
        },
        "workflow": {
            "maximum_repair_rounds": 3,
            "review_axes": ["spec", "standards"],
            "allow_missing_spec": False,
            "release_requires_approval": True,
        },
        "outputs": {"state": ".harness/state", "evidence": ".harness/evidence"},
    }
    save_product(root, product)
    change = {
        "schema_version": 1,
        "change_id": "a",
        "spec_refs": ["openspec/changes/a/proposal.md", "openspec/changes/a/specs/"],
        "write_scope": ["src/", "tests/", "openspec/", "harness/", "docs/"],
        "required_check_ids": ["unit"],
        "dependency_change_ids": [],
        "approval_refs": [],
    }
    (root / "openspec/changes/a/harness.yaml").write_text(yaml.safe_dump(change), encoding="utf-8")
    write_json(
        root,
        "harness/lock.json",
        {
            "schema_version": 1,
            "package_version": "0.1.0",
            "package_digest": digest(b"fixture"),
            "generated": {},
        },
    )
    base = commit(root)
    return root, Git(root, GIT), base, product, change


@pytest.fixture
def product(tmp_path):
    return product_fixture(tmp_path / "product")


def cli(root, *args, stdin=None, env=None):
    return subprocess.run(
        [sys.executable, "-m", "harnesskit", "--root", str(root), "--git", GIT, *args],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, "PYTHONPATH": str(REPO / "src"), **(env or {})},
    )


def test_schema_exports_match_canonical():
    for name, schema in SCHEMAS.items():
        Draft202012Validator.check_schema(schema)
        exported = read_json(REPO / "schemas" / f"{name}.schema.json")
        assert exported.pop("$schema") == "https://json-schema.org/draft/2020-12/schema"
        assert exported == schema


@pytest.mark.parametrize(
    "path",
    [
        "../outside",
        "/etc/passwd",
        "C:/escape",
        "a/../b",
        "a\\b",
        "a:stream",
        "NUL",
        "a//b",
        "a./x",
        "a/{evil}",
    ],
)
def test_relative_path_rejections(tmp_path, path):
    with pytest.raises(HarnessError):
        safe_path(tmp_path, path)


def test_junction_or_symlink_escape(tmp_path):
    root, outside = tmp_path / "root", tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (outside / "secret").write_text("preserve")
    link = root / "link"
    if os.name == "nt":
        subprocess.run(
            [os.environ["COMSPEC"], "/c", "mklink", "/J", str(link), str(outside)],
            check=True,
            capture_output=True,
            timeout=10,
        )
    else:
        link.symlink_to(outside, target_is_directory=True)
    try:
        with pytest.raises(HarnessError, match="linked_path"):
            safe_path(root, "link/secret")
    finally:
        link.rmdir() if os.name == "nt" else link.unlink()
    assert (outside / "secret").read_text() == "preserve"


def test_yaml_duplicate_alias_unknown_and_bad_versions(product):
    root, _, _, data, _ = product
    raw = yaml.safe_dump(data)
    with pytest.raises(HarnessError, match="duplicate"):
        config.yaml_data(raw + "schema_version: 1\n", "project")
    with pytest.raises(HarnessError, match="aliases"):
        config.yaml_data("a: &a x\nb: *a", "project")
    for mutate in (
        lambda x: x.update(unexpected=True),
        lambda x: x.update(schema_version=99),
        lambda x: x["workflow"].update(allow_missing_spec=True),
        lambda x: x["workflow"].update(review_axes=["spec"]),
    ):
        modified = copy.deepcopy(data)
        mutate(modified)
        save_product(root, modified)
        with pytest.raises(HarnessError, match="schema_validation"):
            config.project(root)


def test_policy_union_and_weakening(product):
    root, _, _, product_data, change = product
    extended = copy.deepcopy(product_data)
    extended["verification"]["checks"]["lint"] = {
        "command": [sys.executable, "-c", "print('lint')"],
        "kind": "static",
        "timeout_seconds": 10,
    }
    change["required_check_ids"] = ["lint"]
    (root / "openspec/changes/a/harness.yaml").write_text(yaml.safe_dump(change))
    selected, required = config.select(root, extended, ["a"])
    assert list(selected) == ["a"] and required == ["lint", "unit"]
    assert config.policy(extended, product_data)
    for mutate in (
        lambda x: x["verification"].update(baseline_checks=["lint"]),
        lambda x: x["verification"]["checks"]["unit"].update(command=["fake"]),
        lambda x: x["verification"]["checks"]["unit"].update(allow_skipped=True),
        lambda x: x["verification"]["checks"]["unit"].update(report_format="playwright-json"),
    ):
        modified = copy.deepcopy(extended)
        mutate(modified)
        with pytest.raises(HarnessError):
            config.policy(modified, product_data)


def test_unknown_check_duplicate_change_missing_dependency(product):
    root, _, _, data, change = product
    with pytest.raises(HarnessError, match="duplicate"):
        config.select(root, data, ["a", "a"])
    for field, value, reason in (
        ("required_check_ids", ["missing"], "unknown_check"),
        ("dependency_change_ids", ["b"], "missing_dependency"),
        ("change_id", "wrong", "change_id_mismatch"),
    ):
        broken = {**change, field: value}
        (root / "openspec/changes/a/harness.yaml").write_text(yaml.safe_dump(broken))
        with pytest.raises(HarnessError, match=reason):
            config.select(root, data, ["a"])


@pytest.mark.parametrize(
    "content,reason",
    [
        ("<testsuite tests='0'/>", "insufficient_executed_tests"),
        (
            "<testsuite><testcase name='s'><skipped/></testcase></testsuite>",
            "insufficient_executed_tests",
        ),
        ("<testsuite><testcase name='f'><failure/></testcase></testsuite>", "test_failures"),
        ("<testsuite><testcase name='e'><error/></testcase></testsuite>", "test_failures"),
        (
            "<testsuite><testcase name='p'/><testcase name='s'><skipped/></testcase></testsuite>",
            "skipped_tests_forbidden",
        ),
    ],
)
def test_junit_actual_outcomes(tmp_path, content, reason):
    (tmp_path / "report.xml").write_text(content)
    report, result = parse(tmp_path, "report.xml", "junit")
    assert result == reason
    assert report["tests"] == report["passed"] + report["failed"] + report["skipped"]


@pytest.mark.parametrize(
    "content",
    [
        "PASS",
        "<testsuite tests='9'><testcase name='p'/></testsuite>",
        "<!DOCTYPE x><testsuite/>",
        "<testsuite><testcase/></testsuite>",
        "<testsuite><testcase name='x'/><testcase name='x'/></testsuite>",
    ],
)
def test_junit_lies_and_malformed(tmp_path, content):
    (tmp_path / "report.xml").write_text(content)
    with pytest.raises(HarnessError):
        parse(tmp_path, "report.xml", "junit")


def pw_report(states, status="expected"):
    return {
        "suites": [
            {
                "title": "file",
                "specs": [
                    {
                        "id": "id",
                        "title": "test",
                        "tests": [
                            {
                                "projectName": "chromium",
                                "status": status,
                                "results": [{"status": state} for state in states],
                            }
                        ],
                    }
                ],
            }
        ],
        "errors": [],
    }


@pytest.mark.parametrize(
    "states,status,reason",
    [
        (["passed"], "expected", None),
        (["failed", "passed"], "flaky", "test_failures"),
        (["timedOut"], "unexpected", "test_failures"),
        (["skipped"], "skipped", "insufficient_executed_tests"),
        (["interrupted"], "unexpected", "test_failures"),
    ],
)
def test_playwright_actual_attempts(tmp_path, states, status, reason):
    write_json(tmp_path, "report.json", pw_report(states, status))
    _, parsed_reason = parse(tmp_path, "report.json", "playwright-json")
    assert parsed_reason == reason


def test_playwright_no_results_and_global_errors(tmp_path):
    for data in (
        pw_report([]),
        {**pw_report(["passed"]), "errors": [{"message": "setup failed"}]},
        {"status": "PASS", "stats": {"expected": 100}},
    ):
        write_json(tmp_path, "report.json", data)
        with pytest.raises(HarnessError):
            parse(tmp_path, "report.json", "playwright-json")


def test_runner_argv_stdout_stderr_and_nonzero(tmp_path):
    special = 'literal ; & $(no) `no` " quote'
    result = run(
        tmp_path,
        [
            sys.executable,
            "-c",
            "import sys;print(sys.argv[1]);print('error',file=sys.stderr);sys.exit(7)",
            special,
        ],
        10,
        ".harness/runs/one",
        "unit",
    )
    assert result["status"] == "FAIL" and result["exit_code"] == 7
    assert (tmp_path / result["stdout"]["path"]).read_text().strip() == special
    assert (tmp_path / result["stderr"]["path"]).read_text().strip() == "error"
    assert result["cleanup"] == "complete"


def test_missing_executable_blocked(tmp_path):
    result = run(
        tmp_path, ["harness-test-nonexistent-executable-4567"], 1, ".harness/runs/missing", "unit"
    )
    assert result["status"] == "BLOCKED" and result["cleanup"] == "not_started"


@pytest.mark.parametrize("parent_sleep", [True, False])
def test_timeout_and_normal_exit_clean_descendants(tmp_path, parent_sleep):
    marker = tmp_path / "heartbeat"
    pid_file = tmp_path / "child.pid"
    child = (
        "import pathlib,time,os;"
        f"pathlib.Path({str(pid_file)!r}).write_text(str(os.getpid()));"
        f"p=pathlib.Path({str(marker)!r});"
        "\nwhile True:\n p.write_text(str(time.monotonic()));time.sleep(.03)"
    )
    parent = (
        f"import subprocess,sys,time,pathlib;subprocess.Popen([sys.executable,'-c',{child!r}]);"
        f"p=pathlib.Path({str(pid_file)!r});"
        "\nwhile not p.exists(): time.sleep(.01)\n" + ("time.sleep(60)" if parent_sleep else "")
    )
    started = time.monotonic()
    result = run(tmp_path, [sys.executable, "-c", parent], 1, ".harness/runs/timeout", "unit")
    assert time.monotonic() - started < 8
    assert result["timed_out"] == parent_sleep
    assert result["cleanup"] == "complete"
    assert pid_file.exists()
    first = marker.read_text() if marker.exists() else ""
    time.sleep(0.2)
    assert (marker.read_text() if marker.exists() else "") == first
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x100000, False, int(pid_file.read_text()))
        if handle:
            try:
                assert kernel.WaitForSingleObject(handle, 0) == 0
            finally:
                kernel.CloseHandle(handle)


def test_official_verify_and_ci_claims_rejected(product, monkeypatch):
    root, git, base, _, _ = product
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("CI", "true")
    result = verification.verify(root, git, ["a"], base)
    assert result["status"] == "PASS"
    saved = read_json(root / result["evidence"])
    assert saved["checks"][0]["report"]["passed"] == 1
    assert saved["provenance"] == {"kind": "local", "verified": False}
    assert evidence.inspect(root, git, ["a"], base, result["evidence"])["status"] == "PASS"
    with pytest.raises(HarnessError, match="ci_provenance_provider_unavailable") as blocked:
        evidence.inspect(root, git, ["a"], base, result["evidence"], require_ci=True)
    assert blocked.value.result["status"] == "BLOCKED"
    saved["provenance"] = {"kind": "ci", "verified": True}
    write_json(root, result["evidence"], saved)
    with pytest.raises(HarnessError, match="schema_validation"):
        evidence.inspect(root, git, ["a"], base, result["evidence"])


def test_zero_exit_without_report_fails(tmp_path):
    root, git, base, _, _ = product_fixture(tmp_path / "no-report", "print('PASS')")
    result = verification.verify(root, git, ["a"], base)
    assert result["status"] == "FAIL"
    assert result["checks"][0]["reason"] == "missing_path"


def test_verify_dirty_and_write_scope_gates(product):
    root, git, base, _, _ = product
    (root / "untracked.txt").write_text("dirty")
    with pytest.raises(HarnessError, match="dirty_tree"):
        verification.verify(root, git, ["a"], base)
    commit(root, "outside scope")
    with pytest.raises(HarnessError, match="changed_paths_outside_scope"):
        verification.verify(root, git, ["a"], base)


@pytest.mark.parametrize(
    "target", ["src/app.py", "openspec/changes/a/proposal.md", "harness/lock.json"]
)
def test_stale_candidate_spec_and_lock(product, target):
    root, git, base, _, _ = product
    result = verification.verify(root, git, ["a"], base)
    if target.endswith(".json"):
        lock = read_json(root / target)
        lock["package_digest"] = digest(b"changed")
        write_json(root, target, lock)
    else:
        (root / target).write_text("changed content\n")
    commit(root, "changed candidate")
    inspected = evidence.inspect(root, git, ["a"], base, result["evidence"])
    assert inspected["status"] == "FAIL" and "stale_evidence" in inspected["reasons"]


def test_report_and_log_tampering(product):
    root, git, base, _, _ = product
    result = verification.verify(root, git, ["a"], base)
    check = result["checks"][0]
    (root / check["stdout"]["path"]).write_text("fabricated log")
    inspected = evidence.inspect(root, git, ["a"], base, result["evidence"])
    assert "artifact_hash_mismatch" in inspected["reasons"]
    (root / check["report"]["path"]).write_text("<testsuite/>")
    inspected = evidence.inspect(root, git, ["a"], base, result["evidence"])
    assert "insufficient_executed_tests" in inspected["reasons"]


def test_binding_idempotence_update_conflict_preservation(tmp_path):
    product, templates = tmp_path / "product", tmp_path / "templates"
    product.mkdir()
    templates.mkdir()
    (templates / "source.txt").write_bytes(b"first\n")
    manifest = {
        "schema_version": 1,
        "package_version": "0.1.0",
        "package_digest": digest(b"shared-core-runtime"),
        "files": [
            {"source": "source.txt", "target": "generated.txt", "sha256": digest(b"first\n")}
        ],
    }
    write_json(templates, "binding.json", manifest)
    assert binding.sync(product, templates, "binding.json")["status"] == "PASS"
    assert read_json(product / "harness/lock.json")["package_digest"] == manifest["package_digest"]
    assert manifest["package_digest"] != digest(manifest)
    modified = (product / "generated.txt").stat().st_mtime_ns
    assert binding.sync(product, templates, "binding.json")["changed"] == []
    assert (product / "generated.txt").stat().st_mtime_ns == modified
    (templates / "source.txt").write_bytes(b"second\n")
    manifest["files"][0]["sha256"] = digest(b"second\n")
    write_json(templates, "binding.json", manifest)
    assert binding.sync(product, templates, "binding.json")["status"] == "PASS"
    (product / "generated.txt").write_bytes(b"user edit")
    previous_lock = (product / "harness/lock.json").read_bytes()
    assert binding.check(product)["drift"] == ["generated.txt"]
    result = binding.sync(product, templates, "binding.json")
    assert result["status"] == "FAIL" and not result["changed"]
    assert (product / "generated.txt").read_bytes() == b"user edit"
    assert (product / "harness/lock.json").read_bytes() == previous_lock


def review_files(root, evidence_path):
    data = read_json(root / evidence_path)
    paths = []
    for axis in ("spec", "standards"):
        document = {
            "schema_version": 1,
            "axis": axis,
            "reviewer": f"reviewer-{axis}",
            "implementer": "builder",
            "status": "PASS",
            "fingerprint": data["fingerprint"],
            "evidence_sha256": digest((root / evidence_path).read_bytes()),
            "findings": [],
            "readonly": {"provider": "claimed-read-only", "receipt": "not-a-proof"},
        }
        path = f".harness/{axis}.json"
        write_json(root, path, document)
        paths.append(path)
    return paths


def test_review_axes_and_fake_readonly_receipt(product):
    root, git, base, _, _ = product
    verified = verification.verify(root, git, ["a"], base)
    paths = review_files(root, verified["evidence"])
    result = review.review(root, git, ["a"], base, verified["evidence"], *paths)
    assert result["status"] == "BLOCKED"
    assert all(not value["readonly_verified"] for value in result["axes"].values())
    data = read_json(root / paths[0])
    data["status"] = "FAIL"
    write_json(root, paths[0], data)
    result = review.review(root, git, ["a"], base, verified["evidence"], *paths, local=True)
    assert result["status"] == "FAIL"
    assert result["axes"]["standards"]["status"] == "PASS"
    data["reviewer"] = "builder"
    write_json(root, paths[0], data)
    with pytest.raises(HarnessError, match="independent"):
        review.review(root, git, ["a"], base, verified["evidence"], *paths)


def test_lease_cleanup_preserves_other_change_and_wrong_owner(tmp_path):
    root, registry = tmp_path / "root", tmp_path / "registry"
    root.mkdir()
    a = leases.acquire(root, registry, "p", "a", "task-a", "port-4000")["lease"]
    b = leases.acquire(root, registry, "p", "b", "task-b", "port-4001")["lease"]
    (root / b["directory"] / "data").write_text("preserve")
    with pytest.raises(HarnessError, match="resource_owned"):
        leases.acquire(root, registry, "p", "b", "task-b", "port-4000")
    with pytest.raises(HarnessError, match="ownership_mismatch"):
        leases.release(root, registry, "b", "task-b", a["token"], clean=True)
    leases.release(root, registry, "a", "task-a", a["token"], clean=True)
    assert not (root / a["directory"]).exists()
    assert (root / b["directory"] / "data").read_text() == "preserve"


def hook_event(**changes):
    return {
        "schema_version": 1,
        "adapter": "local-v1",
        "event": "Stop",
        "event_id": "e1",
        "change_id": "a",
        "stop_hook_active": False,
        "interrupted": False,
        "repair_round": 0,
        "budget_remaining": 3,
        "state": "FAIL",
        "unresolved_findings": 1,
        **changes,
    }


def test_hook_reentry_and_interrupt_bounded(tmp_path):
    result = hooks.handle(tmp_path, hook_event())
    assert result["action"] == "continue"
    assert hooks.handle(tmp_path, hook_event())["action"] == "stop"
    for updates in (
        {"stop_hook_active": True},
        {"interrupted": True},
        {"state": "BLOCKED"},
        {"budget_remaining": 0},
        {"repair_round": 3},
        {"event": "Interrupt"},
    ):
        assert hooks.handle(tmp_path, hook_event(event_id="unique", **updates))["action"] == "stop"
    assert result["elapsed_seconds"] < 1


def test_native_hook_stdout_and_exit_semantics(product):
    root, _, _, _, _ = product
    response = cli(
        root, "hook", "--input", "-", stdin=json.dumps(hook_event(adapter="codex-desktop"))
    )
    assert response.returncode == 0
    assert json.loads(response.stdout)["decision"] == "block"
    interrupted = cli(
        root,
        "hook",
        "--input",
        "-",
        stdin=json.dumps(hook_event(adapter="codex-desktop", event="Interrupt")),
    )
    assert interrupted.returncode == 0
    assert set(json.loads(interrupted.stdout)) == {"systemMessage"}
    invalid = cli(
        root,
        "hook",
        "--input",
        "-",
        stdin=json.dumps(hook_event(adapter="codex-desktop", event="InventedEvent")),
    )
    assert invalid.returncode == 0 and "decision" not in json.loads(invalid.stdout)
    assert json.loads(invalid.stderr)["status"] in {"FAIL", "BLOCKED"}


def test_followup_claim_completion_dedup_and_stale_head(product, tmp_path):
    root, git, base, _, _ = product
    event = {
        "schema_version": 1,
        "repository": "owner/repo",
        "pr": 4,
        "change_id": "a",
        "branch": "main",
        "worktree": str(root),
        "owner": "task-a",
        "write_scope": ["src/"],
        "event_id": "event-one",
        "head": base,
        "repair_round": 0,
        "budget_remaining": 2,
        "completed": False,
        "approval_required": False,
    }
    registry = tmp_path / "registry"
    result = followup.handle(root, git, event, registry)
    assert result["action"] == "claimed" and result["schedule"] == "NOT_CONFIGURED"
    with pytest.raises(HarnessError, match="writer_active"):
        followup.handle(root, git, {**event, "event_id": "two"}, registry)
    followup.handle(root, git, event, registry, complete=True, token=result["claim"]["token"])
    assert followup.handle(root, git, event, registry)["action"] == "duplicate"
    with pytest.raises(HarnessError, match="stale_head"):
        followup.handle(root, git, {**event, "head": "0" * 40}, registry)


def test_handoff_and_cli_exit_protocol(product):
    root, git, base, _, _ = product
    verified = verification.verify(root, git, ["a"], base)
    result = handoff.handoff(root, git, "a", base, verified["evidence"], "harnesskit doctor")
    assert result["candidate_refresh_required"] and not result["durable_verified"]
    assert "harnesskit doctor" in (root / result["handoff"]).read_text()
    result = cli(root, "verify", "--change", "a", "--base", base)
    assert result.returncode == 2 and json.loads(result.stdout)["reason"] == "dirty_tree"
    result = cli(root, "verify", "--invented")
    assert result.returncode == 1 and json.loads(result.stdout)["reason"] == "invalid_arguments"


def test_verify_publishes_context_and_invalidates_on_failed_preflight(product):
    root, git, base, _, _ = product
    result = verification.verify(root, git, ["a"], base)
    path = root / ".harness/hooks/verification-context.json"
    context = validate("verification-context", read_json(path))
    assert context["state"] == "PASS" and context["change_id"] == "a"
    assert context["evidence"] == result["evidence"]
    assert context["evidence_sha256"] == digest((root / result["evidence"]).read_bytes())
    assert context["fingerprint"]["head"] == base
    (root / "src/app.py").write_text("dirty")
    with pytest.raises(HarnessError, match="dirty_tree"):
        verification.verify(root, git, ["a"], base)
    assert not path.exists()


def test_failed_report_context_is_real_failure(tmp_path):
    root, git, base, _, _ = product_fixture(tmp_path / "no-report", "print('PASS')")
    result = verification.verify(root, git, ["a"], base)
    context = read_json(root / ".harness/hooks/verification-context.json")
    assert context["state"] == "FAIL" and context["unresolved_findings"] == 1
    assert evidence.inspect(root, git, ["a"], base, result["evidence"])["status"] == "FAIL"


@pytest.mark.parametrize("resource", ["browser", "gpu"])
def test_missing_resource_interface_blocked(product, resource):
    root, git, _, data, _ = product
    data["verification"]["checks"]["unit"]["resources"] = [resource]
    save_product(root, data)
    base = commit(root, "explicit resource contract")
    result = verification.verify(root, git, ["a"], base)
    assert result["status"] == "BLOCKED" and result["checks"][0]["exit_code"] is None
    assert evidence.inspect(root, git, ["a"], base, result["evidence"])["status"] == "BLOCKED"


def test_multi_change_union_executes_shared_check_once(product):
    root, git, _, data, change = product
    path = root / "openspec/changes/b"
    path.mkdir()
    (path / "proposal.md").write_text("second change")
    b = {**change, "change_id": "b", "spec_refs": ["openspec/changes/b/proposal.md"]}
    data["verification"]["checks"]["extra"] = {
        "command": [sys.executable, "-c", "print('extra')"],
        "kind": "static",
        "timeout_seconds": 10,
    }
    b["required_check_ids"] = ["unit", "extra"]
    (path / "harness.yaml").write_text(yaml.safe_dump(b))
    save_product(root, data)
    base = commit(root)
    result = verification.verify(root, git, ["b", "a"], base)
    assert result["status"] == "PASS"
    assert [c["id"] for c in result["checks"]] == ["extra", "unit"]
    context = read_json(root / ".harness/hooks/verification-context.json")
    assert context["change_ids"] == ["a", "b"] and "change_id" not in context


def test_worktree_fingerprint_detects_changes_while_already_dirty(product):
    root, git, base, _, _ = product
    (root / "src/app.py").write_text("first dirty input")
    result = verification.verify(root, git, ["a"], base, local=True)
    assert result["status"] == "PASS"
    assert evidence.inspect(root, git, ["a"], base, result["evidence"])["status"] == "PASS"
    (root / "src/app.py").write_text("second dirty input")
    assert evidence.inspect(root, git, ["a"], base, result["evidence"])["status"] == "FAIL"


def test_candidate_mutation_during_verification_fails(tmp_path):
    code = (
        "import pathlib,os;p=pathlib.Path(os.environ['HARNESS_RUN_DIR'])/'reports/unit.xml';"
        f"p.parent.mkdir(parents=True);p.write_text({XML!r});"
        "pathlib.Path('src/app.py').write_text('command modified source')"
    )
    root, git, base, _, _ = product_fixture(tmp_path / "mutator", code)
    result = verification.verify(root, git, ["a"], base)
    assert result["status"] == "FAIL"
    assert "candidate_changed_during_verification" in result["reasons"]


def test_baseline_policy_mutation_rejected_before_execution(product):
    root, git, base, data, _ = product
    data["verification"]["checks"]["unit"]["command"] = [sys.executable, "-c", "print('fake')"]
    save_product(root, data)
    commit(root, "weaken policy")
    with pytest.raises(HarnessError, match="policy_check_changed"):
        verification.verify(root, git, ["a"], base)
    assert not (root / ".harness/runs").exists()


def test_hidden_git_flags_block_official_verification(product):
    root, git, base, _, _ = product
    git_command(root, "update-index", "--assume-unchanged", "src/app.py")
    (root / "src/app.py").write_text("hidden modification")
    with pytest.raises(HarnessError, match="hidden_index_flags"):
        verification.verify(root, git, ["a"], base)


def test_git_env_cannot_redirect_candidate(product, tmp_path, monkeypatch):
    root, _, base, _, _ = product
    other, other_git, _, _, _ = product_fixture(tmp_path / "other")
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(other))
    git = Git(root, GIT)
    assert git.snapshot(base)["head"] == base
    assert git.root != other_git.root


def test_review_dirty_and_standards_failure_independent(product):
    root, git, base, _, _ = product
    result = verification.verify(root, git, ["a"], base)
    spec, standards = review_files(root, result["evidence"])
    data = read_json(root / standards)
    data["findings"] = [{"id": "open", "resolved": False, "text": "failed standard"}]
    write_json(root, standards, data)
    checked = review.review(root, git, ["a"], base, result["evidence"], spec, standards, local=True)
    assert checked["axes"]["spec"]["status"] == "PASS"
    assert checked["axes"]["standards"]["status"] == "FAIL"
    (root / "src/app.py").write_text("dirty")
    with pytest.raises(HarnessError, match="dirty_tree"):
        review.review(root, git, ["a"], base, result["evidence"], spec, standards)


def test_nonfinite_yaml_and_duplicate_argv(product):
    root, _, _, data, _ = product
    data["verification"]["checks"]["unit"]["timeout_seconds"] = float("nan")
    save_product(root, data)
    with pytest.raises(HarnessError, match="non_json_schema_input"):
        config.project(root)
    data["verification"]["checks"]["unit"]["timeout_seconds"] = 5
    data["verification"]["checks"]["unit"]["command"] = [
        sys.executable,
        "-c",
        "pass",
        "same",
        "same",
    ]
    save_product(root, data)
    assert config.project(root)


@pytest.mark.parametrize("target", [".git/config", ".GIT/config", "harness/LOCK.json", "../escape"])
def test_binding_forbidden_destinations_preserve_product(tmp_path, target):
    root, source = tmp_path / "root", tmp_path / "source"
    root.mkdir()
    source.mkdir()
    (source / "template").write_bytes(b"template")
    manifest = {
        "schema_version": 1,
        "package_version": "0.1.0",
        "package_digest": digest(b"shared-core-runtime"),
        "files": [{"source": "template", "target": target, "sha256": digest(b"template")}],
    }
    write_json(source, "manifest.json", manifest)
    with pytest.raises(HarnessError):
        binding.sync(root, source, "manifest.json")
    assert not list(root.iterdir())


def test_binding_removed_and_deleted_files_conflict(tmp_path):
    root, source = tmp_path / "root", tmp_path / "source"
    root.mkdir()
    source.mkdir()
    (source / "template").write_bytes(b"template")
    manifest = {
        "schema_version": 1,
        "package_version": "0.1.0",
        "package_digest": digest(b"shared-core-runtime"),
        "files": [
            {"source": "template", "target": "a.txt", "sha256": digest(b"template")},
            {"source": "template", "target": "b.txt", "sha256": digest(b"template")},
        ],
    }
    write_json(source, "manifest.json", manifest)
    binding.sync(root, source, "manifest.json")
    (root / "a.txt").unlink()
    result = binding.sync(root, source, "manifest.json")
    assert result["conflicts"] == ["a.txt"] and not (root / "a.txt").exists()
    manifest["files"] = manifest["files"][1:]
    write_json(source, "manifest.json", manifest)
    assert binding.sync(root, source, "manifest.json")["conflicts"] == ["a.txt"]


def test_expired_lease_is_not_stolen_and_corruption_fails(tmp_path):
    root, registry = tmp_path / "root", tmp_path / "registry"
    root.mkdir()
    result = leases.acquire(root, registry, "p", "a", "owner", "resource", ttl=1)
    state = read_json(registry / "leases.json")
    state["leases"]["resource"]["expires"] = 0
    write_json(registry, "leases.json", state)
    with pytest.raises(HarnessError, match="requires_owner_recovery"):
        leases.acquire(root, registry, "p", "b", "other", "resource")
    state["leases"]["resource"]["directory"] = "../outside"
    write_json(registry, "leases.json", state)
    with pytest.raises(HarnessError, match="directory_mismatch"):
        leases.release(root, registry, "a", "owner", result["lease"]["token"], clean=True)


def test_followup_different_pr_cannot_write_same_change(product, tmp_path):
    root, git, base, _, _ = product
    event = {
        "schema_version": 1,
        "repository": "owner/repo",
        "pr": 1,
        "change_id": "a",
        "branch": "main",
        "worktree": str(root),
        "owner": "task",
        "write_scope": ["src/"],
        "event_id": "one",
        "head": base,
        "repair_round": 0,
        "budget_remaining": 2,
        "completed": False,
        "approval_required": False,
    }
    registry = tmp_path / "registry"
    result = followup.handle(root, git, event, registry)
    with pytest.raises(HarnessError, match="change_writer_active"):
        followup.handle(root, git, {**event, "pr": 2}, registry)
    (root / "src/app.py").write_text("repair")
    commit(root, "repair")
    completed = followup.handle(root, git, event, registry, True, result["claim"]["token"])
    assert completed["action"] == "completed"


def test_unsupported_hook_is_blocked(tmp_path):
    with pytest.raises(HarnessError, match="unsupported_hook") as result:
        hooks.handle(tmp_path, hook_event(event="InventedEvent"))
    assert result.value.result["status"] == "BLOCKED"


def test_binding_requires_explicit_package_digest():
    manifest = {
        "schema_version": 1,
        "package_version": "0.1.0",
        "files": [{"source": "x", "target": "x", "sha256": digest(b"x")}],
    }
    with pytest.raises(HarnessError, match="schema_validation"):
        validate("binding", manifest)
    manifest["package_digest"] = "claimed-PASS"
    with pytest.raises(HarnessError, match="schema_validation"):
        validate("binding", manifest)


@pytest.mark.parametrize("passes", [True, False])
def test_real_pytest_junit_report_execution(tmp_path, passes):
    leaf = (
        "import os,pathlib,subprocess,sys;"
        "report=pathlib.Path(os.environ['HARNESS_RUN_DIR'])/'reports/unit.xml';"
        "sys.exit(subprocess.call([sys.executable,'-m','pytest','case_test.py','-q',"
        "'-p','no:cacheprovider','--junitxml',str(report)]))"
    )
    root, git, _, _, _ = product_fixture(tmp_path / "pytest-product", leaf)
    (root / ".gitignore").write_text(".harness/\n__pycache__/\n")
    (root / "case_test.py").write_text(f"def test_actual_assertion():\n    assert {passes!r}\n")
    base = commit(root, "actual pytest test")
    result = verification.verify(root, git, ["a"], base)
    assert result["status"] == ("PASS" if passes else "FAIL")
    report = result["checks"][0]["report"]
    assert report["tests"] == 1
    assert report["failed"] == int(not passes)
    assert report["passed"] == int(passes)
