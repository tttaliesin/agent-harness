"""Reject empty, frozen, malformed and stale decoded stream evidence."""

import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "stream_probe", ROOT / "skills/streaming-testing/scripts/stream_probe.py"
)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


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
