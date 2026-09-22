"""Small filesystem and result primitives shared by the command modules."""

import hashlib
import json
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path, PurePosixPath, PureWindowsPath

EXITS = {"PASS": 0, "FAIL": 1, "BLOCKED": 2}
IDENTIFIER = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,95}\Z")


class HarnessError(Exception):
    def __init__(self, reason, status="FAIL", **details):
        super().__init__(reason)
        self.result = {"status": status, "reason": reason, **details}


def blocked(reason, **details):
    raise HarnessError(reason, "BLOCKED", **details)


def identifier(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value) or value in {".", ".."}:
        raise HarnessError("invalid_identifier", value=value)
    return value


def digest(data):
    if not isinstance(data, bytes):
        data = json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def relative(value, *, template=False, dot=False):
    if not isinstance(value, str) or not value or "\x00" in value or "\\" in value:
        raise HarnessError("invalid_relative_path", path=value)
    check = value.replace("{run_id}", "run") if template else value
    parts = check.rstrip("/").split("/")
    if (
        "{" in check
        or "}" in check
        or PureWindowsPath(check).drive
        or PurePosixPath(check).is_absolute()
        or ":" in check
        or any(p in {"", "..", "."} for p in parts)
        and not (dot and check == ".")
    ):
        raise HarnessError("invalid_relative_path", path=value)
    for part in parts:
        if part.casefold() == ".git":
            raise HarnessError("git_metadata_path_forbidden", path=value)
        if part.endswith((".", " ")) and part != ".":
            raise HarnessError("ambiguous_path", path=value)
        if re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part):
            raise HarnessError("reserved_path", path=value)
    return value


def safe_path(root, value, *, must_exist=False, dot=False):
    relative(value, dot=dot)
    root = Path(root).resolve(strict=True)
    path = root / value
    cursor = root
    for part in Path(value).parts:
        cursor = cursor / part
        # Reject all links/junctions, including links that currently point inside root.
        if cursor.is_symlink() or cursor.is_junction():
            raise HarnessError("linked_path", path=value)
    if not path.resolve().is_relative_to(root):
        raise HarnessError("path_escape", path=value)
    if must_exist and not path.exists():
        raise HarnessError("missing_path", path=value)
    return path


def bytes_at(root, value):
    path = safe_path(root, value, must_exist=True)
    if not path.is_file() or path.stat().st_size > 16 * 1024 * 1024:
        raise HarnessError("invalid_or_oversized_file", path=value)
    return path.read_bytes()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise HarnessError("duplicate_key", key=key)
        result[key] = value
    return result


def read_json(path):
    try:
        if path.stat().st_size > 16 * 1024 * 1024:
            raise HarnessError("oversized_json")
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=unique_pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                HarnessError("invalid_json_number", value=value)
            ),
        )
    except (ValueError, UnicodeError) as exc:
        raise HarnessError("invalid_json", detail=str(exc)) from exc


def atomic_write(root, value, data):
    path = safe_path(root, value)
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_path(root, value)
    payload = data if isinstance(data, bytes) else data.encode("utf-8")
    fd, temp = tempfile.mkstemp(prefix=".harness-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        safe_path(root, value)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def write_json(root, value, data):
    atomic_write(root, value, json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n")


@contextmanager
def exclusive(root, value):
    """Fail closed on concurrent access; never guess that a surviving lock is stale."""
    path = safe_path(root, value)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        blocked("state_busy", path=value)
    try:
        os.write(descriptor, str(os.getpid()).encode())
        yield
    finally:
        os.close(descriptor)
        path.unlink()


def aggregate(statuses):
    values = set(statuses)
    if "FAIL" in values:
        return "FAIL"
    if not values or values - {"PASS"}:
        return "BLOCKED"
    return "PASS"
