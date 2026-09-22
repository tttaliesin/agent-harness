"""Canonical version-one schemas; schemas/*.json are generated exports."""

import json

from jsonschema import Draft202012Validator

from .common import HarnessError


def obj(properties, required=None):
    return {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
        "required": list(properties) if required is None else required,
    }


def array(items, minimum=0):
    return {"type": "array", "items": items, "minItems": minimum, "uniqueItems": True}


STRING = {"type": "string", "minLength": 1}
ID = {"type": "string", "pattern": r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,95}$"}
SHA = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
COMMIT = {"type": "string", "pattern": "^(?:[0-9a-f]{40}|[0-9a-f]{64})$"}
VERSION = {"const": 1}
STATUS = {"enum": ["PASS", "FAIL", "BLOCKED", "NOT_RUN", "NOT_APPLICABLE"]}
BOOL = {"type": "boolean"}
COUNT = {"type": "integer", "minimum": 0}
ARGV = {"type": "array", "items": STRING, "minItems": 1}
PATHS = array(STRING)
HASHES = {"type": "object", "additionalProperties": SHA}
CHECK = obj(
    {
        "command": ARGV,
        "kind": {"enum": ["structural", "static", "tests"]},
        "timeout_seconds": {"type": "number", "exclusiveMinimum": 0, "maximum": 86400},
        "report": STRING,
        "report_format": {"enum": ["junit", "playwright-json"]},
        "minimum_tests": {"type": "integer", "minimum": 1},
        "allow_skipped": BOOL,
        "required_tools": PATHS,
        "resources": array({"enum": ["browser", "gpu"]}),
    },
    ["command", "kind", "timeout_seconds"],
)
CHECK["allOf"] = [
    {
        "if": {"properties": {"kind": {"const": "tests"}}},
        "then": {"required": ["report", "report_format", "minimum_tests"]},
    }
]
PROJECT = obj(
    {
        "schema_version": VERSION,
        "project": obj({"id": ID, "root": {"const": "."}, "packs": array(ID)}),
        "documents": obj(
            {
                key: STRING
                for key in ("agents", "domain", "architecture", "decisions", "tracker", "specs")
            }
        ),
        "verification": obj(
            {
                "baseline_checks": array(ID, 1),
                "checks": {
                    "type": "object",
                    "minProperties": 1,
                    "propertyNames": ID,
                    "additionalProperties": CHECK,
                },
            }
        ),
        "workflow": obj(
            {
                "maximum_repair_rounds": {"type": "integer", "minimum": 0, "maximum": 10},
                "review_axes": {
                    "type": "array",
                    "items": {"enum": ["spec", "standards"]},
                    "minItems": 2,
                    "maxItems": 2,
                    "uniqueItems": True,
                },
                "allow_missing_spec": {"const": False},
                "release_requires_approval": {"const": True},
            }
        ),
        "outputs": obj({"state": STRING, "evidence": STRING}),
    }
)
CHANGE = obj(
    {
        "schema_version": VERSION,
        "change_id": ID,
        "spec_refs": array(STRING, 1),
        "write_scope": array(STRING, 1),
        "required_check_ids": array(ID),
        "dependency_change_ids": array(ID),
        "approval_refs": PATHS,
    }
)
LOCK = obj(
    {
        "schema_version": VERSION,
        "package_version": STRING,
        "package_digest": SHA,
        "generated": HASHES,
    }
)
MANIFEST = obj(
    {
        "schema_version": VERSION,
        "package_version": STRING,
        "package_digest": SHA,
        "files": array(obj({"source": STRING, "target": STRING, "sha256": SHA}), 1),
    }
)
FINGERPRINT = obj(
    {
        "head": COMMIT,
        "base": COMMIT,
        "tree": COMMIT,
        "dirty": BOOL,
        "worktree": SHA,
        "project": SHA,
        "policy": SHA,
        "changes": HASHES,
        "specs": HASHES,
        "locks": HASHES,
        "checks": SHA,
    }
)
REPORT = obj(
    {
        "format": {"enum": ["junit", "playwright-json"]},
        "path": STRING,
        "sha256": SHA,
        "tests": COUNT,
        "passed": COUNT,
        "failed": COUNT,
        "skipped": COUNT,
    }
)
ARTIFACT = obj({"path": STRING, "sha256": SHA})
EXECUTION = obj(
    {
        "id": ID,
        "status": STATUS,
        "reason": STRING,
        "argv": ARGV,
        "cwd": STRING,
        "started": STRING,
        "finished": STRING,
        "exit_code": {"type": ["integer", "null"]},
        "timed_out": BOOL,
        "cleanup": {"enum": ["complete", "not_started", "failed"]},
        "stdout": ARTIFACT,
        "stderr": ARTIFACT,
        "report": REPORT,
    },
    [
        "id",
        "status",
        "argv",
        "cwd",
        "started",
        "finished",
        "exit_code",
        "timed_out",
        "cleanup",
        "stdout",
        "stderr",
    ],
)
EVIDENCE = obj(
    {
        "schema_version": VERSION,
        "project_id": ID,
        "change_ids": array(ID, 1),
        "run_id": ID,
        "purpose": {"enum": ["local", "official"]},
        "status": STATUS,
        "fingerprint": FINGERPRINT,
        "required_checks": array(ID, 1),
        "checks": array(EXECUTION),
        "environment": obj({"os": STRING, "python": STRING, "git": STRING, "packs": array(ID)}),
        "provenance": obj({"kind": {"const": "local"}, "verified": {"const": False}}),
        "reasons": PATHS,
    }
)
REVIEW = obj(
    {
        "schema_version": VERSION,
        "axis": {"enum": ["spec", "standards"]},
        "reviewer": ID,
        "implementer": ID,
        "status": STATUS,
        "fingerprint": FINGERPRINT,
        "evidence_sha256": SHA,
        "findings": array(obj({"id": ID, "resolved": BOOL, "text": STRING})),
        "readonly": obj({"provider": STRING, "receipt": STRING}),
    }
)
HOOK = obj(
    {
        "schema_version": VERSION,
        "adapter": {"enum": ["local-v1", "codex-desktop"]},
        "event": {"enum": ["SessionStart", "Stop", "SubagentStop", "Interrupt"]},
        "event_id": ID,
        "change_id": ID,
        "stop_hook_active": BOOL,
        "interrupted": BOOL,
        "repair_round": COUNT,
        "budget_remaining": COUNT,
        "state": STATUS,
        "unresolved_findings": COUNT,
    }
)
FOLLOWUP = obj(
    {
        "schema_version": VERSION,
        "repository": STRING,
        "pr": {"type": "integer", "minimum": 1},
        "change_id": ID,
        "branch": STRING,
        "worktree": STRING,
        "owner": ID,
        "write_scope": array(STRING, 1),
        "event_id": ID,
        "head": COMMIT,
        "repair_round": COUNT,
        "budget_remaining": COUNT,
        "completed": BOOL,
        "approval_required": BOOL,
    }
)
VERIFICATION_CONTEXT = obj(
    {
        "schema_version": VERSION,
        "change_ids": array(ID, 1),
        "change_id": ID,
        "state": {"enum": ["PASS", "FAIL", "BLOCKED"]},
        "unresolved_findings": COUNT,
        "fingerprint": FINGERPRINT,
        "evidence": STRING,
        "evidence_sha256": SHA,
        "provenance": obj({"kind": {"const": "local"}, "verified": {"const": False}}),
    },
    [
        "schema_version",
        "change_ids",
        "state",
        "unresolved_findings",
        "fingerprint",
        "evidence",
        "evidence_sha256",
        "provenance",
    ],
)

TOKEN = {"type": "string", "pattern": "^[0-9a-f]{48}$"}
LEASE = obj(
    {
        "project_id": ID,
        "change_id": ID,
        "owner": ID,
        "resource": ID,
        "token": TOKEN,
        "worktree": STRING,
        "directory": STRING,
        "created": {"type": "number", "minimum": 0},
        "expires": {"type": "number", "minimum": 0},
        "allocator_pid": COUNT,
        "namespace": STRING,
        "kind": {"const": "cooperative_local"},
        "readiness_verified": {"const": False},
    }
)
LEASE_STATE = obj(
    {
        "schema_version": VERSION,
        "leases": {"type": "object", "propertyNames": ID, "additionalProperties": LEASE},
    }
)
CLAIM = obj({"token": TOKEN, "owner": ID, "event_key": SHA, "worktree": STRING})
FOLLOWUP_STATE = obj({"done": array(SHA), "active": {"anyOf": [CLAIM, {"type": "null"}]}})

SCHEMAS = {
    "project": PROJECT,
    "change": CHANGE,
    "lock": LOCK,
    "binding": MANIFEST,
    "evidence": EVIDENCE,
    "review": REVIEW,
    "hook": HOOK,
    "followup": FOLLOWUP,
    "verification-context": VERIFICATION_CONTEXT,
    "lease-state": LEASE_STATE,
    "followup-state": FOLLOWUP_STATE,
}


def validate(name, data):
    try:
        json.dumps(data, allow_nan=False)
    except (ValueError, TypeError, RecursionError) as exc:
        raise HarnessError("non_json_schema_input", detail=str(exc)) from exc
    errors = sorted(Draft202012Validator(SCHEMAS[name]).iter_errors(data), key=str)
    if errors:
        error = errors[0]
        raise HarnessError(
            "schema_validation",
            schema=name,
            path="/".join(map(str, error.absolute_path)),
            detail=error.message,
        )
    return data
