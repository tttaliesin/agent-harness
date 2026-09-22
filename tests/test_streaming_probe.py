"""Reject empty, frozen, malformed and stale decoded stream evidence."""

import importlib.util
import json
import os
import socket
import subprocess
import sys
import threading
import time
from argparse import Namespace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "stream_probe", ROOT / "skills/streaming-testing/scripts/stream_probe.py"
)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)
FIXTURE_SPEC = importlib.util.spec_from_file_location(
    "stream_fixture", ROOT / "fixtures/streaming/run.py"
)
fixture_module = importlib.util.module_from_spec(FIXTURE_SPEC)
FIXTURE_SPEC.loader.exec_module(fixture_module)


def transcript(hashes=("a", "b", "c", "d")):
    return "#format: frame checksums\n#hash: MD5\n" + "\n".join(
        f"0, {n}, {n}, 1, 86400, {value * 32}" for n, value in enumerate(hashes)
    )


def test_decoded_frames_supply_count_and_distinct_hashes():
    result = probe.require_frames(probe.parse_frames(transcript()), minimum=4)
    assert result["frames"] == 4
    assert result["unique_frames"] == 4
    assert result["first_pts"] == 0
    assert result["last_pts"] == 3


@pytest.mark.parametrize("text", ["", "PASS", "#hash: MD5\n", "0, 0, 0, 1, 0, nope"])
def test_missing_or_malformed_frames_fail(text):
    with pytest.raises(probe.ProbeError):
        probe.require_frames(probe.parse_frames(text), minimum=4)


def test_advancing_timestamps_with_frozen_pixels_fail():
    with pytest.raises(probe.ProbeError, match="distinct"):
        probe.require_frames(probe.parse_frames(transcript(("a",) * 8)))


def test_replayed_pre_outage_frames_do_not_prove_recovery():
    before = probe.parse_frames(transcript())
    with pytest.raises(probe.ProbeError, match="new"):
        probe.require_frames(probe.parse_frames(transcript()), minimum=4, previous=before)


def test_nonadvancing_timestamps_fail():
    with pytest.raises(probe.ProbeError, match="timestamp"):
        probe.parse_frames(transcript().replace("0, 2, 2,", "0, 1, 1,"))


def test_timeout_terminates_decoder_before_return():
    started = time.monotonic()
    result = probe.receive([sys.executable, "-c", "import time; time.sleep(2)"], timeout=0.1)
    assert result.get("timed_out") is True
    assert result["returncode"] != 0
    assert time.monotonic() - started < 1.5


def test_missing_tool_is_blocked(tmp_path):
    result = probe.probe(tmp_path / "missing-ffmpeg", "rtsp://127.0.0.1:1/test")
    assert result["status"] == "BLOCKED"


def test_cli_missing_tool_returns_blocked_report(tmp_path):
    report = tmp_path / "result.json"
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            SPEC.origin,
            "rtsp://127.0.0.1:1/test",
            "--ffmpeg",
            str(tmp_path / "missing"),
            "--output",
            str(report),
        ],
        capture_output=True,
        timeout=5,
    )
    assert result.returncode == 2
    assert json.loads(report.read_text())["status"] == "BLOCKED"


def test_failed_rerun_cannot_overwrite_previous_report(tmp_path):
    report = tmp_path / "result.json"
    report.write_text('{"status":"PASS"}')
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            SPEC.origin,
            "rtsp://127.0.0.1:1/test",
            "--ffmpeg",
            str(tmp_path / "missing"),
            "--output",
            str(report),
        ],
        capture_output=True,
        timeout=5,
    )
    assert result.returncode != 0
    assert report.read_text() == '{"status":"PASS"}'


def test_cleanup_preserves_another_tasks_process(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "stream_fixture", ROOT / "fixtures/streaming/run.py"
    )
    fixture_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture_module)
    owned = fixture_module.Fixture(tmp_path)
    other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(10)"])
    try:
        child = owned.start("test-decoder", [sys.executable, "-c", "import time; time.sleep(10)"])
        result = owned.close()
        assert result["status"] == "PASS"
        assert child.poll() is not None
        assert other.poll() is None
    finally:
        owned.close()
        other.kill()
        other.wait(timeout=5)


def test_unsampled_old_epoch_is_rejected_even_with_new_hashes(tmp_path, monkeypatch):
    before = probe.parse_frames(transcript())
    unsampled = transcript(("e", "f", "1", "2"))
    assert probe.require_frames(probe.parse_frames(unsampled), 4, before)["new_frames"] == 4

    def decode(command, timeout):
        # Boundary substitute for FFmpeg: newly sampled moving frames of the old red epoch.
        if "-f" in command and command[-1] != "-":
            Path(command[-1]).write_bytes(bytes([253, 0, 0]) * 16 * 16 * 4)
        return {"stdout": unsampled, "stderr": "", "returncode": 0, "timed_out": False}

    monkeypatch.setattr(probe, "receive", decode)
    result = probe.probe("ffmpeg", "rtsp://127.0.0.1:1/fixture", frames=4, expected_marker="blue")
    assert result["status"] == "FAIL"
    assert "blue" in result["reason"]


@pytest.mark.parametrize("response", [404, 500, 200])
def test_outage_observes_whole_window_after_fast_decoder_exit(tmp_path, response):
    calls = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            calls.append(time.monotonic())
            self.send_response(response)
            self.end_headers()
            self.wfile.write(b'{"ready":true}')

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    owned = fixture_module.Fixture(tmp_path)
    live = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(10)"])
    started = time.monotonic()
    try:
        url = f"http://127.0.0.1:{server.server_port}/path"
        if response == 404:
            owned.observe_outage(live, url, started, duration=0.3)
            assert time.monotonic() - started >= 0.3
            assert len(calls) >= 3
        else:
            with pytest.raises((fixture_module.probe.ProbeError, OSError)):
                owned.observe_outage(live, url, started, duration=0.3)
    finally:
        owned.close()
        live.kill()
        live.wait(timeout=5)
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_prerequisite_permission_is_blocked(tmp_path, monkeypatch, capsys):
    # A directory as the executable causes a real OS launch denial on Windows and POSIX.
    monkeypatch.setattr(fixture_module, "HERE", tmp_path)
    result = fixture_module.run(Namespace(ffmpeg=str(tmp_path), mediamtx="missing", webrtc=False))
    report = json.loads(capsys.readouterr().out)
    assert result == 2
    assert report["status"] == "BLOCKED"


def test_driver_exit_does_not_release_ownership_of_descendants(tmp_path):
    address = tmp_path / "listener.json"
    listener = (
        "import socket,time,json,os,pathlib; s=socket.socket(); "
        "s.bind(('127.0.0.1',0)); s.listen(); "
        f"pathlib.Path({str(address)!r}).write_text(json.dumps([os.getpid(),s.getsockname()[1]])); "
        "time.sleep(20)"
    )
    driver = (
        f"import subprocess; subprocess.Popen([{sys.executable!r},'-c',{listener!r}], "
        "stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)"
    )
    owned = fixture_module.Fixture(tmp_path)
    descendant_pid = None
    port = None
    try:
        parent = owned.start("browser", [sys.executable, "-c", driver])
        parent.wait(timeout=5)
        deadline = time.monotonic() + 5
        while not address.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        descendant_pid, port = json.loads(address.read_text())
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            pass
        report = owned.close()
        with socket.socket() as sock:
            assert sock.connect_ex(("127.0.0.1", port)) != 0
        assert report["status"] == "PASS"
        assert report["survivors"] == []
    finally:
        owned.close()
        if descendant_pid is not None and port is not None:
            with socket.socket() as sock:
                if sock.connect_ex(("127.0.0.1", port)) == 0:
                    # Only the test's positively observed orphan, never a name-wide cleanup.
                    os.kill(descendant_pid, 15)


@pytest.mark.parametrize(
    "dirty,changed,expected",
    [
        (False, False, "a" * 40),
        (True, False, None),
        (False, True, None),
    ],
)
def test_source_attribution_requires_clean_stable_revision(dirty, changed, expected):
    start = {
        "status": "OBSERVED",
        "revision": "a" * 40,
        "dirty": dirty,
        "runtime_sha256": {"run.py": "initial"},
    }
    finish = {**start, "runtime_sha256": {"run.py": "changed"}} if changed else dict(start)
    result = fixture_module.source_attribution(start, finish)
    assert result["committed_candidate"] == expected


def test_decoder_runtime_permission_error_is_failure(monkeypatch):
    def failing_receive(command, timeout):
        raise PermissionError("runtime output access lost")

    monkeypatch.setattr(probe, "receive", failing_receive)
    assert probe.probe("ffmpeg", "rtsp://127.0.0.1:1/test")["status"] == "FAIL"


def test_cleanup_reports_survivors_even_when_parent_exited(tmp_path, monkeypatch):
    owned = fixture_module.Fixture(tmp_path)
    child = owned.start("finished", [sys.executable, "-c", "pass"])
    child.wait(timeout=5)
    # Simulate the OS still reporting a surviving member after attempted termination.
    monkeypatch.setattr(owned, "stop", lambda process: None)
    monkeypatch.setattr(owned, "survivors", lambda process: [123456])
    result = owned.close()
    assert result["status"] == "FAIL"
    assert result["survivors"] == [{"name": "finished", "member": 123456}]


@pytest.mark.parametrize("color", ["red", "blue"])
def test_decoded_epoch_marker_accepts_matching_color(color):
    pixel = bytes([253, 0, 0]) if color == "red" else bytes([0, 0, 254])
    result = probe.require_marker(pixel * 16 * 16 * 4, color, 4)
    assert result["frames"] == 4
    assert all(sample["matched_fraction"] == 1 for sample in result["samples"])


@pytest.mark.parametrize("pixels", [b"", bytes([0, 0, 255]) * 16 * 16 * 3])
def test_missing_marker_frames_fail(pixels):
    with pytest.raises(probe.ProbeError):
        probe.require_marker(pixels, "blue", 4)


def test_owned_tool_launch_denial_is_blocked_and_cleaned(tmp_path):
    owned = fixture_module.Fixture(tmp_path)
    try:
        with pytest.raises(fixture_module.probe.ToolUnavailable):
            owned.start("denied", [str(tmp_path)])
    finally:
        report = owned.close()
    assert report["status"] == "PASS"
    assert report["survivors"] == []


@pytest.mark.parametrize("code,report", [(1, {"status": "PASS"}), (0, []), (0, {"status": "FAIL"})])
def test_browser_runtime_failure_cannot_become_pass(code, report):
    with pytest.raises(fixture_module.probe.ProbeError):
        fixture_module.accept_browser_result(code, report)


def test_browser_launch_block_is_preserved():
    with pytest.raises(fixture_module.probe.ToolUnavailable):
        fixture_module.accept_browser_result(2, {"status": "BLOCKED", "reason": "access denied"})
