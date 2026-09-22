"""Content-hash ownership for explicitly supplied, byte-for-byte templates."""

from .common import (
    HarnessError,
    atomic_write,
    bytes_at,
    digest,
    exclusive,
    read_json,
    safe_path,
    write_json,
)
from .schema import validate


def load_lock(root, path="harness/lock.json"):
    return validate("lock", read_json(safe_path(root, path, must_exist=True)))


def check(root, lock_path="harness/lock.json"):
    lock = load_lock(root, lock_path)
    drift = []
    for name, expected in lock["generated"].items():
        path = safe_path(root, name)
        if not path.is_file() or digest(bytes_at(root, name)) != expected:
            drift.append(name)
    return {
        "status": "FAIL" if drift else "PASS",
        "drift": drift,
        "package_digest": lock["package_digest"],
    }


def sync(root, template_root, manifest_path, lock_path="harness/lock.json"):
    manifest = validate(
        "binding", read_json(safe_path(template_root, manifest_path, must_exist=True))
    )
    desired = {}
    aliases = set()
    for entry in manifest["files"]:
        target = entry["target"]
        safe_path(root, target)
        if (
            target.casefold() in aliases
            or target.casefold() == lock_path.casefold()
            or target.split("/")[0].casefold() in {".git", ".harness"}
        ):
            raise HarnessError("invalid_binding_target", path=target)
        aliases.add(target.casefold())
        content = bytes_at(template_root, entry["source"])
        if digest(content) != entry["sha256"]:
            raise HarnessError("template_hash_mismatch", path=entry["source"])
        desired[target] = content
    for target in aliases:
        if any(other.startswith(target.rstrip("/") + "/") for other in aliases - {target}):
            raise HarnessError("overlapping_binding_targets")
    for target in desired:
        path = safe_path(root, target)
        if any(parent.exists() and not parent.is_dir() for parent in path.parents):
            raise HarnessError("binding_parent_not_directory", path=target)
    # One product writer; preflight every conflict before replacing any generated content.
    with exclusive(root, ".harness/binding.lock"):
        lock_file = safe_path(root, lock_path)
        previous = load_lock(root, lock_path)["generated"] if lock_file.exists() else {}
        conflicts = sorted(set(previous) - desired.keys())
        changed = []
        for target, content in desired.items():
            path = safe_path(root, target)
            current = digest(bytes_at(root, target)) if path.exists() else None
            new = digest(content)
            if current is not None and current != new and current != previous.get(target):
                conflicts.append(target)
            elif current is None and target in previous:
                conflicts.append(target)  # A user deletion is also an edit.
            elif current != new:
                changed.append(target)
        if conflicts:
            return {
                "status": "FAIL",
                "reason": "binding_conflict",
                "conflicts": conflicts,
                "changed": [],
            }
        for target in changed:
            atomic_write(root, target, desired[target])
        lock = {
            "schema_version": 1,
            "package_version": manifest["package_version"],
            "package_digest": manifest["package_digest"],
            "generated": {name: digest(data) for name, data in desired.items()},
        }
        if not lock_file.exists() or read_json(lock_file) != lock:
            write_json(root, lock_path, lock)
            changed.append(lock_path)
    return {"status": "PASS", "changed": changed, "package_digest": lock["package_digest"]}
