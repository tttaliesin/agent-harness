"""Actual native JSON entry and bounded continuation behavior."""

import json
import os
import subprocess
import sys

from test_core import product_fixture

from harnesskit import native_hook, verification


def invoke(root, event):
    env = dict(os.environ)
    return subprocess.run(
        [sys.executable, "-m", "harnesskit.native_hook"],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        timeout=12,
        check=True,
    )


def event(root, kind="Stop", turn="turn-1"):
    return {
        "cwd": str(root),
        "session_id": "session-1",
        "turn_id": turn,
        "hook_event_name": kind,
        "stop_hook_active": False,
    }


def test_non_product_no_action(tmp_path):
    assert json.loads(invoke(tmp_path, event(tmp_path)).stdout) == {}


def test_interrupt_and_reentry_do_not_resume(tmp_path):
    root, _, _, _, _ = product_fixture(tmp_path / "product")
    interrupted = json.loads(invoke(root, event(root, "Interrupt")).stdout)
    assert set(interrupted) == {"systemMessage"}
    repeated = event(root)
    repeated["stop_hook_active"] = True
    assert json.loads(invoke(root, repeated).stdout) == {}


def test_session_start_is_native_context(tmp_path):
    root, _, _, _, _ = product_fixture(tmp_path / "product")
    output = json.loads(invoke(root, event(root, "SessionStart")).stdout)
    assert output["hookSpecificOutput"]["hookEventName"] == "SessionStart"


def test_bad_context_never_blocks_native_stop(tmp_path):
    root, _, _, _, _ = product_fixture(tmp_path / "product")
    path = root / ".harness/hooks/verification-context.json"
    path.parent.mkdir(parents=True)
    path.write_text('{"state":"PASS"}')
    result = json.loads(invoke(root, event(root)).stdout)
    assert "decision" not in result


def test_failed_real_check_continues_once_per_event_with_session_budget(tmp_path):
    root, git, base, _, _ = product_fixture(tmp_path / "product", "raise SystemExit(1)")
    verification.verify(root, git, ["a"], base, local=True)
    first = json.loads(invoke(root, event(root)).stdout)
    assert first["decision"] == "block"
    assert "decision" not in json.loads(invoke(root, event(root)).stdout)
    for number in [2, 3]:
        assert (
            json.loads(invoke(root, event(root, turn=f"turn-{number}")).stdout)["decision"]
            == "block"
        )
    assert "decision" not in json.loads(invoke(root, event(root, turn="turn-4")).stdout)


def test_stale_verification_does_not_request_continuation(tmp_path):
    root, git, base, _, _ = product_fixture(tmp_path / "product", "raise SystemExit(1)")
    verification.verify(root, git, ["a"], base, local=True)
    (root / "src/app.py").write_text("changed after verification")
    assert "decision" not in json.loads(invoke(root, event(root)).stdout)


def test_subagent_cannot_inherit_product_continuation(tmp_path):
    root, _, _, _, _ = product_fixture(tmp_path / "product")
    assert "decision" not in native_hook.adapt(event(root, "SubagentStop"), root)
