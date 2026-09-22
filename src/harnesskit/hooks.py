"""Bounded local event handling; Desktop wrappers adapt native inputs explicitly."""

import time

from .common import HarnessError, blocked, exclusive, read_json, safe_path, write_json
from .schema import validate


def handle(root, event, maximum_repair_rounds=3):
    if isinstance(event, dict) and (
        event.get("adapter") not in {"local-v1", "codex-desktop"}
        or event.get("event") not in {"SessionStart", "Stop", "SubagentStop", "Interrupt"}
    ):
        blocked("unsupported_hook_adapter_or_event")
    validate("hook", event)
    started = time.monotonic()
    native = event["adapter"] == "codex-desktop"
    result = {"status": "PASS", "action": "stop", "reason": "no_continuation_needed"}
    output = {}
    if event["event"] == "Interrupt" or event["interrupted"]:
        result["reason"] = "interrupted"
        # Interrupt allows only systemMessage and cannot restart the turn.
        output = {"systemMessage": "Harness recorded interruption; no continuation requested."}
    else:
        with exclusive(root, ".harness/hooks/handler.lock"):
            path = ".harness/hooks/events.json"
            file = safe_path(root, path)
            history = read_json(file) if file.exists() else []
            if not isinstance(history, list) or len(history) > 256:
                raise HarnessError("invalid_hook_history")
            key = f"{event['change_id']}:{event['event']}:{event['event_id']}"
            stop = (
                event["stop_hook_active"]
                or key in history
                or event["state"] == "BLOCKED"
                or event["repair_round"] >= maximum_repair_rounds
                or event["budget_remaining"] == 0
            )
            if stop:
                result["reason"] = "reentry_blocked_or_budget_exhausted"
            elif event["event"] in {"Stop", "SubagentStop"} and (
                event["state"] == "FAIL" or event["unresolved_findings"]
            ):
                result.update(
                    action="continue", reason="Review current findings within the repair budget."
                )
                output = {"decision": "block", "reason": result["reason"]}
            elif event["event"] == "SessionStart":
                result["reason"] = "session_diagnostic"
                output = {
                    "systemMessage": "Harness adapter ready; run harnesskit doctor for status."
                }
            if stop:
                output = {"continue": False, "systemMessage": result["reason"]}
            if key not in history:
                write_json(root, path, (history + [key])[-256:])
    result["elapsed_seconds"] = time.monotonic() - started
    result["native_acceptance"] = "NOT_RUN"
    write_json(root, ".harness/hooks/latest.json", result)
    return output if native else result
