"""Cooperative filesystem leases. No daemon, service lifecycle or PID-based deletion."""

import os
import secrets
import shutil
import time
from pathlib import Path

from .common import (
    HarnessError,
    blocked,
    digest,
    exclusive,
    identifier,
    read_json,
    safe_path,
    write_json,
)
from .schema import validate


def registry_root(value):
    path = Path(value).absolute()
    for item in [path, *path.parents]:
        if item.is_symlink() or item.is_junction():
            raise HarnessError("linked_registry")
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve(strict=True)


def _state(registry):
    path = safe_path(registry, "leases.json")
    state = read_json(path) if path.exists() else {"schema_version": 1, "leases": {}}
    validate("lease-state", state)
    if any(key != record["resource"] for key, record in state["leases"].items()):
        raise HarnessError("lease_key_mismatch")
    return state


def acquire(root, registry, project_id, change_id, owner, resource, ttl=3600):
    for value in (project_id, change_id, owner, resource):
        identifier(value)
    if not 1 <= ttl <= 86400:
        raise HarnessError("invalid_lease_ttl")
    registry = registry_root(registry)
    root = Path(root).resolve(strict=True)
    namespace = f"{project_id}-{change_id}-{digest(str(root))[:12]}"
    with exclusive(registry, "registry.lock"):
        state = _state(registry)
        existing = state["leases"].get(resource)
        if existing:
            blocked(
                "lease_expired_requires_owner_recovery"
                if existing["expires"] <= time.time()
                else "resource_owned",
                resource=resource,
                owner=existing["owner"],
            )
        token = secrets.token_hex(24)
        directory = f".harness/resources/{namespace}/{token}"
        record = {
            "project_id": project_id,
            "change_id": change_id,
            "owner": owner,
            "resource": resource,
            "token": token,
            "worktree": str(root),
            "directory": directory,
            "created": time.time(),
            "expires": time.time() + ttl,
            "allocator_pid": os.getpid(),
            "namespace": namespace,
            "kind": "cooperative_local",
            "readiness_verified": False,
        }
        safe_path(root, directory).mkdir(parents=True)
        write_json(root, f"{directory}/owner.json", record)
        state["leases"][resource] = record
        write_json(registry, "leases.json", state)
    return {"status": "PASS", "lease": record}


def _owned(root, state, change_id, owner, token):
    records = [r for r in state["leases"].values() if r["token"] == token]
    if len(records) != 1:
        raise HarnessError("unknown_lease_token")
    record = records[0]
    if (
        record["change_id"] != change_id
        or record["owner"] != owner
        or record["worktree"] != str(Path(root).resolve())
    ):
        raise HarnessError("lease_ownership_mismatch")
    namespace = f"{record['project_id']}-{change_id}-{digest(record['worktree'])[:12]}"
    expected = f".harness/resources/{namespace}/{token}"
    if record["directory"] != expected:
        raise HarnessError("lease_directory_mismatch")
    marker = read_json(safe_path(root, f"{expected}/owner.json", must_exist=True))
    if marker != record:
        raise HarnessError("resource_marker_mismatch")
    return record


def release(root, registry, change_id, owner, token, *, clean=False):
    root = Path(root).resolve(strict=True)
    for value in (change_id, owner, token):
        identifier(value)
    registry = registry_root(registry)
    with exclusive(registry, "registry.lock"):
        state = _state(registry)
        record = _owned(root, state, change_id, owner, token)
        if clean:
            directory = safe_path(root, record["directory"], must_exist=True)
            # Inspect every descendant before shutil.rmtree; never traverse a symlink/junction.
            for current, dirs, files in os.walk(directory, followlinks=False):
                for name in dirs + files:
                    safe_path(root, (Path(current) / name).relative_to(root).as_posix())
            safe_path(root, record["directory"], must_exist=True)
            shutil.rmtree(directory)
        del state["leases"][record["resource"]]
        write_json(registry, "leases.json", state)
    return {
        "status": "PASS",
        "released": record["resource"],
        "removed": [record["directory"]] if clean else [],
        "preserved": [] if clean else [record["directory"]],
    }
