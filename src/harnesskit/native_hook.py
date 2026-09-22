"""Adapt native Codex events without promoting local state to trusted evidence."""

import json
import sys
import uuid
from pathlib import Path

from . import config, evidence, hooks
from .common import (
    HarnessError,
    bytes_at,
    digest,
    exclusive,
    read_json,
    safe_path,
    unique_pairs,
    write_json,
)
from .git import Git
from .process import run
from .schema import validate

EVENTS = {"SessionStart", "Stop", "SubagentStop", "Interrupt"}


def inspect_context(root):
    context = validate(
        "verification-context",
        read_json(safe_path(root, ".harness/hooks/verification-context.json")),
    )
    raw = bytes_at(root, context["evidence"])
    if digest(raw) != context["evidence_sha256"]:
        raise HarnessError("hook_evidence_hash_mismatch")
    data = validate("evidence", json.loads(raw, object_pairs_hook=unique_pairs))
    if len(context["change_ids"]) != 1:
        raise HarnessError("hook_requires_one_change_owner")
    _, _, _, current = evidence.context(
        root,
        Git(root),
        context["change_ids"],
        context["fingerprint"]["base"],
        list(context["fingerprint"]["locks"]),
    )
    if current != context["fingerprint"] or current != data["fingerprint"]:
        raise HarnessError("stale_hook_context")
    if context["state"] != data["status"] or context["change_ids"] != data["change_ids"]:
        raise HarnessError("hook_context_mismatch")
    if current["dirty"]:
        raise HarnessError("dirty_hook_context")
    return context


def adapt(native, root):
    event = native.get("hook_event_name")
    if event not in EVENTS or not (root / "harness/project.yaml").is_file():
        return {}
    if event == "Interrupt":
        return {"systemMessage": "Harness interrupted; no continuation requested."}
    if event == "SessionStart":
        return {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "Use project-workflow and the product's existing checks. "
                "Run harnesskit doctor; local evidence cannot approve CI or deployment.",
            }
        }
    if native.get("stop_hook_active") is True:
        return {}
    if native.get("stop_hook_active") not in {True, False, None}:
        raise HarnessError("invalid_native_stop_hook_active")
    if not isinstance(native.get("session_id"), str) or not native["session_id"]:
        raise HarnessError("missing_native_session_id")
    if not isinstance(native.get("turn_id"), str) or not native["turn_id"]:
        raise HarnessError("missing_native_turn_id")
    if event == "SubagentStop":
        # A product-wide verification context cannot establish a subagent's write ownership.
        return {"systemMessage": "Harness leaves subagent completion with its owning task."}
    if not safe_path(root, ".harness/hooks/verification-context.json").is_file():
        return {}
    key = digest([native["session_id"], native["turn_id"], event])
    # A managed subprocess bounds expensive repository fingerprinting and kills descendants.
    result = run(
        root,
        [sys.executable, "-m", "harnesskit.native_hook", "--inspect-context"],
        3,
        ".harness/hooks",
        f"native-{uuid.uuid4().hex}",
    )
    if result["status"] != "PASS":
        return {
            "systemMessage": "Harness hook context is stale, blocked, or exceeded its budget; "
            "run verification explicitly. No continuation requested."
        }
    context = validate(
        "verification-context",
        json.loads(
            bytes_at(root, result["stdout"]["path"]),
            object_pairs_hook=unique_pairs,
        ),
    )
    maximum = config.project(root)["workflow"]["maximum_repair_rounds"]
    session = digest(native["session_id"])
    with exclusive(root, ".harness/hooks/native.lock"):
        state_path = ".harness/hooks/native-rounds.json"
        file = safe_path(root, state_path)
        state = read_json(file) if file.exists() else {}
        if not isinstance(state, dict) or len(state) > 256:
            raise HarnessError("invalid_native_hook_state")
        rounds = state.get(session, 0)
        if type(rounds) is not int or rounds < 0:
            raise HarnessError("invalid_native_hook_rounds")
        mapped = {
            "schema_version": 1,
            "adapter": "codex-desktop",
            "event": event,
            "event_id": key,
            "change_id": context["change_ids"][0],
            "stop_hook_active": False,
            "interrupted": False,
            "repair_round": rounds,
            "budget_remaining": max(0, maximum - rounds),
            "state": context["state"],
            "unresolved_findings": context["unresolved_findings"],
        }
        output = hooks.handle(root, mapped, maximum)
        if output.get("decision") == "block":
            state[session] = rounds + 1
            write_json(root, state_path, dict(list(state.items())[-256:]))
        return output


def main():
    try:
        if sys.argv[1:] == ["--inspect-context"]:
            print(json.dumps(inspect_context(Path.cwd())))
            return 0
        raw = sys.stdin.read(65537)
        if len(raw) > 65536:
            raise HarnessError("native_hook_input_too_large")
        native = json.loads(raw, object_pairs_hook=unique_pairs)
        if not isinstance(native, dict) or not isinstance(native.get("cwd"), str):
            raise HarnessError("invalid_native_hook_input")
        root = Path(native["cwd"]).resolve(strict=True)
        if not root.is_dir():
            raise HarnessError("invalid_native_hook_cwd")
        output = adapt(native, root)
    except (HarnessError, OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Harness native hook BLOCKED: {exc}", file=sys.stderr)
        if sys.argv[1:] == ["--inspect-context"]:
            return 1
        output = {"systemMessage": "Harness hook is blocked; no continuation requested."}
    print(json.dumps(output))
    # Native exit 2 can resume an agent; failures must be represented without that exit.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
