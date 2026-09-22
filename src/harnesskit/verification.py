"""Select the required union, execute it once, and preserve native execution evidence."""

import os
import platform
import sys
import uuid

from . import config
from .common import (
    HarnessError,
    aggregate,
    blocked,
    bytes_at,
    digest,
    exclusive,
    read_json,
    safe_path,
    write_json,
)
from .evidence import context
from .process import executable, now, run
from .reports import parse
from .schema import validate


def verify(root, git, change_ids, base, locks=None, local=False):
    if os.environ.get("HARNESS_ACTIVE_VERIFY"):
        blocked("recursive_verification")
    with exclusive(root, ".harness/verify.lock"):
        previous = safe_path(root, ".harness/hooks/verification-context.json")
        if previous.exists():
            previous.unlink()
        return _verify(root, git, change_ids, base, locks, local)


def _verify(root, git, change_ids, base, locks=None, local=False):
    product, changes, required, fingerprint = context(root, git, change_ids, base, locks)
    git.ignored_outputs()
    if not local:
        git.require_clean()
        scopes = [scope for data in changes.values() for scope in data["write_scope"]]
        uncovered = [path for path in git.changed(base) if not config.covers(path, scopes)]
        if uncovered:
            raise HarnessError("changed_paths_outside_scope", paths=uncovered)
    run_id = uuid.uuid4().hex
    run_dir = f".harness/runs/{run_id}"
    safe_path(root, run_dir).mkdir(parents=True)
    env = {
        **os.environ,
        "HARNESS_RUN_ID": run_id,
        "HARNESS_RUN_DIR": str(safe_path(root, run_dir)),
        "HARNESS_ACTIVE_VERIFY": "1",
    }
    checks = []
    for check_id in required:
        definition = product["verification"]["checks"][check_id]
        prerequisite = None
        if definition.get("resources"):
            prerequisite = "resource_probe_provider_unavailable"
        for tool in definition.get("required_tools", []):
            try:
                executable([tool])
            except HarnessError:
                prerequisite = "required_tool_missing"
        if prerequisite:
            result = {
                "id": check_id,
                "argv": definition["command"],
                "cwd": str(git.root),
                "started": now(),
                "finished": now(),
                "exit_code": None,
                "timed_out": False,
                "cleanup": "not_started",
                "status": "BLOCKED",
                "reason": prerequisite,
            }
            for name in ("stdout", "stderr"):
                path = f"{run_dir}/{check_id}.{name}.log"
                safe_path(root, path).write_bytes(b"")
                result[name] = {"path": path, "sha256": digest(b"")}
        else:
            result = run(
                root,
                definition["command"],
                definition["timeout_seconds"],
                run_dir,
                check_id,
                env=env,
            )
        if definition["kind"] == "tests" and result["exit_code"] is not None:
            report_path = definition["report"].replace("{run_id}", run_id)
            try:
                result["report"], reason = parse(
                    root,
                    report_path,
                    definition["report_format"],
                    definition["minimum_tests"],
                    definition.get("allow_skipped", False),
                )
                if reason and result["status"] == "PASS":
                    result.update(status="FAIL", reason=reason)
            except HarnessError as exc:
                if result["status"] == "PASS":
                    result.update(status="FAIL", reason=exc.result["reason"])
        checks.append(result)
    reasons = []
    _, _, _, after = context(root, git, change_ids, base, locks)
    if after != fingerprint or (not local and after["dirty"]):
        reasons.append("candidate_changed_during_verification")
    evidence = {
        "schema_version": 1,
        "project_id": product["project"]["id"],
        "change_ids": sorted(change_ids),
        "run_id": run_id,
        "purpose": "local" if local else "official",
        "status": "FAIL" if reasons else aggregate(c["status"] for c in checks),
        "fingerprint": fingerprint,
        "required_checks": required,
        "checks": checks,
        "environment": {
            "os": platform.platform(),
            "python": sys.version,
            "git": git.call("--version").strip(),
            "packs": product["project"]["packs"],
        },
        "provenance": {"kind": "local", "verified": False},
        "reasons": reasons,
    }
    validate("evidence", evidence)
    path = f"{product['outputs']['evidence']}/{run_id}.json"
    write_json(root, path, evidence)
    # Publish context only after reading the saved, validated execution evidence.
    persisted = validate("evidence", read_json(safe_path(root, path, must_exist=True)))
    hook_context = {
        "schema_version": 1,
        "change_ids": persisted["change_ids"],
        "state": persisted["status"],
        "unresolved_findings": sum(c["status"] == "FAIL" for c in persisted["checks"]),
        "fingerprint": persisted["fingerprint"],
        "evidence": path,
        "evidence_sha256": digest(bytes_at(root, path)),
        "provenance": persisted["provenance"],
    }
    if len(change_ids) == 1:
        hook_context["change_id"] = change_ids[0]
    validate("verification-context", hook_context)
    write_json(root, ".harness/hooks/verification-context.json", hook_context)
    return {
        "status": evidence["status"],
        "evidence": path,
        "run_id": run_id,
        "provenance": evidence["provenance"],
        "reasons": reasons,
        "checks": checks,
    }
