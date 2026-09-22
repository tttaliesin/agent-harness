"""Run isolated CPU RTSP publish, outage, recovery and optional browser receive."""

import argparse
import importlib.util
import json
import os
import signal
import socket
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "stream_probe", HERE.parents[1] / "skills/streaming-testing/scripts/stream_probe.py"
)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class Fixture:
    def __init__(self, output):
        self.output = output
        self.processes = []
        self.commands = []
        self.http = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def start(self, name, command, env=None):
        log = (self.output / f"{name}.log").open("w", encoding="utf-8")
        try:
            child = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=HERE,
                env=env,
                start_new_session=os.name != "nt",
            )
        except BaseException:
            log.close()
            raise
        self.processes.append((name, child, log))
        self.commands.append({"name": name, "pid": child.pid, "argv": command})
        return child

    def stop(self, child):
        if child.poll() is None:
            owned_name = next(name for name, process, _ in self.processes if process is child)
            if os.name == "nt" and owned_name == "browser":
                # PID is from this invocation's live Popen handle; never match names/ports.
                subprocess.run(
                    ["taskkill", "/PID", str(child.pid), "/T", "/F"],
                    capture_output=True,
                    timeout=5,
                    check=False,
                )
            elif os.name == "nt":
                # The two native media binaries do not spawn child processes.
                child.terminate()
            else:
                os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                if os.name == "nt":
                    child.kill()
                else:
                    os.killpg(child.pid, signal.SIGKILL)
                child.wait(timeout=5)

    def close(self):
        errors = []
        for name, child, log in reversed(self.processes):
            try:
                self.stop(child)
            except (OSError, subprocess.SubprocessError) as error:
                errors.append(f"{name}: {error}")
            finally:
                log.close()
        return {
            "status": "FAIL" if errors else "PASS",
            "errors": errors,
            "processes": [
                {"name": name, "pid": child.pid, "returncode": child.poll()}
                for name, child, _ in self.processes
            ],
        }

    def api(self, url):
        with self.http.open(url, timeout=1) as response:
            return json.load(response)

    def wait_path(self, server, url, expected, timeout=10):
        deadline = time.monotonic() + timeout
        last = None
        while time.monotonic() < deadline:
            if server.poll() is not None:
                raise probe.ProbeError("MediaMTX exited; inspect mediamtx.log")
            try:
                last = self.api(url)
                if last.get("ready") is expected:
                    return last
            except urllib.error.HTTPError as error:
                if error.code == 404 and expected is False:
                    return {"ready": False, "http_status": 404}
                last = str(error)
            except (OSError, ValueError) as error:
                last = str(error)
            time.sleep(0.1)
        raise probe.ProbeError(f"path readiness timeout (expected {expected}): {last}")


def publisher(ffmpeg, url, color):
    # A new solid corner distinguishes source epochs even if testsrc2 time restarts.
    return [
        ffmpeg,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "warning",
        "-re",
        "-f",
        "lavfi",
        "-i",
        "testsrc2=size=320x180:rate=15",
        "-vf",
        f"drawbox=x=0:y=0:w=64:h=64:color={color}:t=fill",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-tune",
        "zerolatency",
        "-profile:v",
        "baseline",
        "-pix_fmt",
        "yuv420p",
        "-g",
        "15",
        "-bf",
        "0",
        "-threads",
        "1",
        "-t",
        "90",
        "-f",
        "rtsp",
        "-rtsp_transport",
        "tcp",
        url,
    ]


def run(args):
    output = HERE / ".reports" / f"run-{uuid.uuid4().hex}"
    output.mkdir(parents=True)
    fixture = Fixture(output)
    result = {
        "status": "FAIL",
        "scope": "CPU synthetic media transport",
        "gpu_inference": "NOT_RUN",
        "tracker_identity": "NOT_RUN",
        "webrtc": {"status": "NOT_RUN"},
        "output": str(output.relative_to(HERE)),
    }
    held = []
    try:
        ffmpeg = str(Path(args.ffmpeg).resolve())
        mediamtx = str(Path(args.mediamtx).resolve())
        versions = {}
        for name, executable, flag, expected in [
            ("ffmpeg", ffmpeg, "-version", "ffmpeg version 8.0-"),
            ("mediamtx", mediamtx, "--version", "v1.15.6"),
        ]:
            version = subprocess.run([executable, flag], capture_output=True, text=True, timeout=5)
            if version.returncode or not version.stdout.startswith(expected):
                raise probe.ProbeError(f"expected pinned {name}: {expected}; got {version.stdout}")
            versions[name] = version.stdout.splitlines()[0]
        result["versions"] = versions
        if args.webrtc and not (HERE / "node_modules/playwright/package.json").is_file():
            raise FileNotFoundError("fixture Playwright dependency; run the pinned install first")
        ports = {}
        for name in ("rtsp", "api", "http", "udp"):
            sock = socket.socket(type=socket.SOCK_DGRAM if name == "udp" else socket.SOCK_STREAM)
            sock.bind(("127.0.0.1", 0))
            held.append(sock)
            ports[name] = sock.getsockname()[1]
        stream = "synthetic-" + uuid.uuid4().hex
        result.update(ports=ports, stream=stream)
        config = output / "mediamtx.yml"
        config.write_text((HERE / "mediamtx.yml.in").read_text().format(**ports, stream=stream))
        # Native MediaMTX does not accept inherited sockets. A bind race fails this run;
        # it never stops the competing process or attaches to its stream.
        for sock in held:
            sock.close()
        held.clear()
        env = {
            key: value for key, value in os.environ.items() if not key.upper().startswith("MTX_")
        }
        server = fixture.start("mediamtx", [mediamtx, str(config)], env)
        path_url = f"http://127.0.0.1:{ports['api']}/v3/paths/get/{stream}"
        fixture.wait_path(server, path_url, False)
        rtsp_url = f"rtsp://127.0.0.1:{ports['rtsp']}/{stream}"
        source = fixture.start("publisher-before", publisher(ffmpeg, rtsp_url, "red"))
        result["ready_before"] = fixture.wait_path(server, path_url, True)
        before = probe.probe(ffmpeg, rtsp_url)
        save(output / "rtsp-before.json", before)
        if before["status"] != "PASS":
            raise probe.ProbeError(f"initial receive: {before.get('reason')}")
        result["before"] = probe.require_frames(before["decoded"], 12)
        fixture.stop(source)
        outage_started = time.monotonic()
        fixture.wait_path(server, path_url, False)
        outage = probe.probe(ffmpeg, rtsp_url, timeout=3)
        save(output / "rtsp-outage.json", outage)
        if (
            outage.get("timed_out")
            or not outage.get("returncode")
            or "404 Not Found" not in outage.get("stderr", "")
            or probe.parse_frames(outage.get("stdout", ""))
        ):
            raise probe.ProbeError("outage did not produce a live-server 404 with zero frames")
        # Verify absence over the whole outage window, not merely once after stopping.
        while time.monotonic() - outage_started < 2:
            if fixture.api(path_url).get("ready") is not False:
                raise probe.ProbeError("source became ready during the forced outage")
            time.sleep(0.1)
        result["outage"] = {
            "status": "PASS",
            "received_frames": 0,
            "seconds": round(time.monotonic() - outage_started, 3),
        }
        recovery_started = time.monotonic()
        fixture.start("publisher-after", publisher(ffmpeg, rtsp_url, "blue"))
        result["ready_after"] = fixture.wait_path(server, path_url, True)
        after = probe.probe(ffmpeg, rtsp_url)
        save(output / "rtsp-after.json", after)
        if after["status"] != "PASS":
            raise probe.ProbeError(f"recovery receive: {after.get('reason')}")
        result["recovery"] = probe.require_frames(after["decoded"], 12, before["decoded"])
        result["recovery"]["seconds"] = round(time.monotonic() - recovery_started, 3)
        if args.webrtc:
            browser_env = dict(
                os.environ, PLAYWRIGHT_BROWSERS_PATH=str(args.browser_cache.resolve())
            )
            browser = fixture.start(
                "browser",
                [
                    args.node,
                    str(HERE / "browser-receive.mjs"),
                    f"http://127.0.0.1:{ports['http']}/{stream}",
                    str(output / "webrtc.json"),
                ],
                browser_env,
            )
            browser.wait(timeout=45)
            browser_report = output / "webrtc.json"
            if not browser_report.is_file():
                raise probe.ProbeError("browser produced no report; inspect browser.log")
            result["webrtc"] = json.loads(browser_report.read_text(encoding="utf-8"))
            if browser.returncode or result["webrtc"].get("status") != "PASS":
                result["status"] = result["webrtc"].get("status", "FAIL")
                raise probe.ProbeError("browser receive failed or blocked; inspect webrtc.json")
        result["status"] = "PASS"
    except FileNotFoundError as error:
        result.update(status="BLOCKED", reason=f"missing tool: {error}")
    except (OSError, subprocess.SubprocessError, ValueError, probe.ProbeError) as error:
        result["reason"] = str(error)
    finally:
        for sock in held:
            sock.close()
        result["cleanup"] = fixture.close()
        if result["cleanup"]["status"] != "PASS":
            result["status"] = "FAIL"
        save(output / "commands.json", fixture.commands)
        save(output / "result.json", result)
    print(json.dumps(result, indent=2))
    return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[result["status"]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ffmpeg", required=True, help="Path to pinned FFmpeg 8.0 executable")
    parser.add_argument("--mediamtx", required=True, help="Path to MediaMTX v1.15.6 executable")
    parser.add_argument("--webrtc", action="store_true", help="Require real browser receive")
    parser.add_argument("--node", default="node")
    parser.add_argument(
        "--browser-cache",
        type=Path,
        default=HERE / ".reports/browsers",
        help="Existing task-local Playwright browser cache; never installs",
    )
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
