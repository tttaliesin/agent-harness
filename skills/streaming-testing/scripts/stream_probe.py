"""Bounded decoded-frame evidence for one explicitly selected RTSP source."""

import argparse
import json
import re
import subprocess
import time
from pathlib import Path


class ProbeError(Exception):
    pass


def parse_frames(text):
    frames = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        fields = [part.strip() for part in line.split(",")]
        if len(fields) != 6 or not re.fullmatch(r"[a-f0-9]{32}", fields[-1]):
            raise ProbeError("malformed framemd5 row")
        try:
            stream, dts, pts, duration, size = map(int, fields[:5])
        except ValueError as error:
            raise ProbeError("malformed framemd5 numbers") from error
        if stream != 0 or size <= 0 or duration <= 0:
            raise ProbeError("invalid decoded video frame")
        if frames and pts <= frames[-1]["pts"]:
            raise ProbeError("nonadvancing frame timestamp")
        frames.append({"pts": pts, "md5": fields[-1]})
    return frames


def require_frames(frames, minimum=8, previous=()):
    if minimum < 4:
        raise ProbeError("minimum must be at least 4")
    if len(frames) < minimum:
        raise ProbeError(f"received {len(frames)} frames; need {minimum}")
    hashes = {frame["md5"] for frame in frames}
    if len(hashes) < 4:
        raise ProbeError("need at least 4 distinct decoded frames")
    old = {frame["md5"] for frame in previous}
    if previous and len(hashes - old) < 4:
        raise ProbeError("recovery lacks 4 new decoded frames")
    return {
        "frames": len(frames),
        "unique_frames": len(hashes),
        "new_frames": len(hashes - old),
        "first_pts": frames[0]["pts"],
        "last_pts": frames[-1]["pts"],
    }


def receive(command, timeout):
    """Capture one decoder; it has no subprocesses of its own."""
    with subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    ) as process:
        timed_out = False
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            stdout, stderr = process.communicate(timeout=5)
        except BaseException:
            process.kill()
            process.wait(timeout=5)
            raise
    return {
        "stdout": stdout,
        "stderr": stderr,
        "returncode": process.returncode,
        "timed_out": timed_out,
    }


def probe(ffmpeg, url, frames=12, timeout=12):
    if not 4 <= frames <= 300 or not 0 < timeout <= 120:
        raise ProbeError("frames must be 4..300 and timeout must be >0..120 seconds")
    command = [
        str(ffmpeg),
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-rtsp_transport",
        "tcp",
        "-timeout",
        str(int(timeout * 1_000_000)),
        "-analyzeduration",
        "1000000",
        "-i",
        url,
        "-map",
        "0:v:0",
        "-an",
        "-frames:v",
        str(frames),
        "-fps_mode",
        "passthrough",
        "-f",
        "framemd5",
        "-",
    ]
    started = time.monotonic()
    try:
        result = receive(command, timeout)
    except OSError as error:
        return {"status": "BLOCKED", "reason": str(error), "command": command}
    result.update(command=command, elapsed_seconds=round(time.monotonic() - started, 3))
    try:
        if result.get("timed_out"):
            raise ProbeError("decoder timeout")
        if result["returncode"]:
            raise ProbeError(f"decoder exit {result['returncode']}")
        result["decoded"] = parse_frames(result["stdout"])
        result.update(require_frames(result["decoded"], frames))
        result["status"] = "PASS"
    except ProbeError as error:
        result.update(status="FAIL", reason=str(error))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Explicitly authorized RTSP source (avoid embedded secrets)")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--frames", type=int, default=12)
    parser.add_argument("--timeout", type=float, default=12)
    parser.add_argument("--output", type=Path, required=True, help="New JSON file; never overwrite")
    args = parser.parse_args()
    # Reserve the output first so a previous PASS can never survive a failed rerun.
    with args.output.open("x", encoding="utf-8") as output:
        try:
            result = probe(args.ffmpeg, args.url, args.frames, args.timeout)
        except ProbeError as error:
            result = {"status": "FAIL", "reason": str(error)}
        json.dump(result, output, indent=2)
    print(json.dumps({"status": result["status"], "output": str(args.output)}))
    return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
