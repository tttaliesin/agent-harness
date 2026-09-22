"""Atomic event/head dedup and one-writer claims; the caller performs bounded work."""

from pathlib import Path

from . import config
from .common import HarnessError, blocked, digest, exclusive, read_json, safe_path, write_json
from .schema import validate
from .workspace import registry_root


def handle(root, git, event, registry, complete=False, token=None):
    validate("followup", event)
    product = config.project(root)
    change = config.change(root, event["change_id"], product["documents"]["specs"])
    if Path(event["worktree"]).resolve() != git.root:
        raise HarnessError("followup_worktree_mismatch")
    if not complete and event["head"] != git.call("rev-parse", "HEAD").strip():
        raise HarnessError("followup_stale_head")
    if event["branch"] != git.call("symbolic-ref", "--short", "HEAD").strip():
        raise HarnessError("followup_branch_mismatch")
    for scope in event["write_scope"]:
        safe_path(root, scope)
        if not config.covers(scope.rstrip("/"), change["write_scope"]):
            raise HarnessError("followup_scope_escape")
    registry = registry_root(registry)
    key = digest({"repository": event["repository"], "pr": event["pr"]})
    event_key = digest({"event_id": event["event_id"], "head": event["head"]})
    path = f"followup/{key}.json"
    common_dir = (git.root / git.call("rev-parse", "--git-common-dir").strip()).resolve()
    writer_path = (
        f"writers/{digest({'repository': str(common_dir), 'change': event['change_id']})}.json"
    )
    with exclusive(registry, "followup.lock"):
        file = safe_path(registry, path)
        state = read_json(file) if file.exists() else {"done": [], "active": None}
        validate("followup-state", state)
        active = state["active"]
        if complete:
            if not active or (
                active["token"] != token
                or active["event_key"] != event_key
                or active["owner"] != event["owner"]
                or active["worktree"] != str(git.root)
            ):
                raise HarnessError("followup_claim_mismatch")
            writer_file = safe_path(registry, writer_path, must_exist=True)
            writer = read_json(writer_file)
            if writer.get("token") != token:
                blocked("followup_writer_claim_mismatch")
            state["done"].append(event_key)
            state["active"] = None
            write_json(registry, path, state)
            writer_file.unlink()
            return {"status": "PASS", "action": "completed", "schedule": "NOT_CONFIGURED"}
        if event_key in state["done"]:
            return {"status": "PASS", "action": "duplicate", "schedule": "NOT_CONFIGURED"}
        if active:
            blocked("followup_writer_active", owner=active["owner"])
        if safe_path(registry, writer_path).exists():
            blocked("followup_change_writer_active")
        if (
            event["completed"]
            or event["approval_required"]
            or not event["budget_remaining"]
            or event["repair_round"] >= product["workflow"]["maximum_repair_rounds"]
        ):
            blocked("followup_stop_condition")
        import secrets

        claim = {
            "token": secrets.token_hex(24),
            "owner": event["owner"],
            "event_key": event_key,
            "worktree": str(git.root),
        }
        state["active"] = claim
        write_json(registry, writer_path, claim)
        write_json(registry, path, state)
    return {"status": "PASS", "action": "claimed", "claim": claim, "schedule": "NOT_CONFIGURED"}
