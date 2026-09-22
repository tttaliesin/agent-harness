"""Independent review axes; claimed sandbox strings cannot grant official approval."""

from .common import HarnessError, aggregate, bytes_at, digest, read_json, safe_path
from .evidence import inspect
from .schema import validate


def review(
    root, git, change_ids, base, evidence_path, spec_path, standards_path, locks=None, local=False
):
    git.require_clean()
    evidence = inspect(root, git, change_ids, base, evidence_path, locks)
    if evidence["status"] != "PASS":
        return {
            "status": evidence["status"],
            "reason": "review_evidence_not_current",
            "evidence": evidence,
        }
    document = read_json(safe_path(root, evidence_path, must_exist=True))
    if document["purpose"] != "official":
        raise HarnessError("official_verification_required_for_review")
    results = {}
    reviewers = set()
    implementers = set()
    for axis, path in (("spec", spec_path), ("standards", standards_path)):
        data = validate("review", read_json(safe_path(root, path, must_exist=True)))
        if data["axis"] != axis:
            raise HarnessError("review_axis_mismatch", axis=axis)
        if data["fingerprint"] != evidence["fingerprint"] or data["evidence_sha256"] != digest(
            bytes_at(root, evidence_path)
        ):
            raise HarnessError("stale_review", axis=axis)
        reviewers.add(data["reviewer"])
        implementers.add(data["implementer"])
        status = data["status"]
        if any(not finding["resolved"] for finding in data["findings"]):
            status = "FAIL"
        reasons = []
        if status == "PASS" and not local:
            status = "BLOCKED"
            reasons.append("readonly_enforcement_provider_unavailable")
        results[axis] = {
            "status": status,
            "reported_status": data["status"],
            "reviewer": data["reviewer"],
            "findings": data["findings"],
            "reasons": reasons,
            "readonly_verified": False,
        }
    if len(reviewers) != 2 or len(implementers) != 1 or reviewers & implementers:
        raise HarnessError("reviewers_not_independent")
    git.require_clean()
    return {
        "status": aggregate(result["status"] for result in results.values()),
        "axes": results,
        "provenance": "local",
        "official": False,
    }
