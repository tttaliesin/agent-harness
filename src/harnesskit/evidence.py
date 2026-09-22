"""Input fingerprints and local artifact revalidation, with an explicit trust boundary."""

from . import config
from .binding import load_lock
from .common import HarnessError, aggregate, blocked, bytes_at, digest, read_json, safe_path
from .reports import parse
from .schema import validate


def context(root, git, change_ids, base, locks=None):
    product = config.project(root)
    changes, required = config.select(root, product, change_ids)
    try:
        baseline_text = git.base_file(base, "harness/project.yaml")
    except HarnessError as exc:
        if exc.result["reason"] == "git_failed":
            blocked("trusted_baseline_policy_unavailable")
        raise
    baseline = config.yaml_data(baseline_text, "project")
    policy_digest = config.policy(product, baseline)
    lock_paths = ["harness/lock.json", *(locks or [])]
    lock_paths = list(dict.fromkeys(lock_paths))
    if len(set(lock_paths)) != len(lock_paths):
        raise HarnessError("duplicate_lock_paths")
    load_lock(root)
    snapshot = git.snapshot(base)
    fingerprint = {
        **snapshot,
        "project": digest(product),
        "policy": policy_digest,
        "changes": {key: digest(value) for key, value in changes.items()},
        "specs": config.spec_hashes(root, changes),
        "locks": {p: digest(bytes_at(root, p)) for p in sorted(lock_paths)},
        "checks": digest({key: product["verification"]["checks"][key] for key in required}),
    }
    return product, changes, required, fingerprint


def inspect(root, git, change_ids, base, evidence_path, locks=None, require_ci=False):
    data = validate("evidence", read_json(safe_path(root, evidence_path, must_exist=True)))
    product, _, required, current = context(root, git, change_ids, base, locks)
    reasons = []
    if data["fingerprint"] != current:
        reasons.append("stale_evidence")
    if data["project_id"] != product["project"]["id"] or data["change_ids"] != sorted(change_ids):
        reasons.append("evidence_identity_mismatch")
    if data["required_checks"] != required:
        reasons.append("required_check_mismatch")
    actual_ids = [c["id"] for c in data["checks"]]
    if sorted(actual_ids) != required:
        reasons.append("executed_check_mismatch")
    statuses = []
    for execution in data["checks"]:
        check_id = execution["id"]
        definition = product["verification"]["checks"].get(check_id)
        if not definition:
            reasons.append("unknown_executed_check")
            continue
        statuses.append(execution["status"])
        if execution["argv"] != definition["command"] or execution["cwd"] != str(git.root):
            reasons.append("execution_input_mismatch")
        if execution["status"] == "PASS" and (
            execution["exit_code"] != 0
            or execution["timed_out"]
            or execution["cleanup"] != "complete"
        ):
            reasons.append("unsuccessful_execution")
        run_prefix = f".harness/runs/{data['run_id']}/"
        for stream in ("stdout", "stderr"):
            artifact = execution[stream]
            if (
                not artifact["path"].startswith(run_prefix)
                or digest(bytes_at(root, artifact["path"])) != artifact["sha256"]
            ):
                reasons.append("artifact_hash_mismatch")
        if definition["kind"] == "tests" and (
            execution["status"] == "PASS" or "report" in execution
        ):
            path = definition["report"].replace("{run_id}", data["run_id"])
            report, reason = parse(
                root,
                path,
                definition["report_format"],
                definition["minimum_tests"],
                definition.get("allow_skipped", False),
            )
            if report != execution.get("report") or (reason and execution["status"] == "PASS"):
                reasons.append(reason or "report_mismatch")
    derived = aggregate(statuses)
    if data["reasons"]:
        reasons.extend(data["reasons"])
    if data["status"] != derived and not data["reasons"]:
        reasons.append("aggregate_status_mismatch")
    if reasons:
        return {
            "status": "FAIL",
            "reasons": sorted(set(reasons)),
            "provenance": data["provenance"],
            "evidence": evidence_path,
        }
    if require_ci:
        blocked("ci_provenance_provider_unavailable", evidence=evidence_path, local_status=derived)
    return {
        "status": derived,
        "reasons": [],
        "provenance": data["provenance"],
        "evidence": evidence_path,
        "fingerprint": current,
    }
