"""Run isolated CPU RTSP publish, outage, recovery and optional browser receive."""

import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
import signal
import socket
import subprocess
import sys
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


def source_snapshot():
    root = Path(__file__).resolve().parents[2]
    git = ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root)]
    try:
        revision = subprocess.run(
            git + ["rev-parse", "HEAD"], capture_output=True, text=True, timeout=5, check=True
        ).stdout.strip()
        status = subprocess.run(
            git + ["status", "--porcelain=v1", "--untracked-files=all"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        ).stdout
        paths = [
            "fixtures/streaming/run.py",
            "fixtures/streaming/browser-receive.mjs",
            "fixtures/streaming/mediamtx.yml.in",
            "fixtures/streaming/package.json",
            "fixtures/streaming/pnpm-lock.yaml",
            "skills/streaming-testing/scripts/stream_probe.py",
        ]
        return {
            "status": "OBSERVED",
            "revision": revision,
            "dirty": bool(status),
            "runtime_sha256": {
                path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in paths
            },
        }
    except (OSError, subprocess.SubprocessError) as error:
        return {"status": "UNAVAILABLE", "reason": str(error)}


def source_attribution(start, finish):
    stable = start.get("status") == "OBSERVED" and start == finish
    committed = stable and start.get("dirty") is False
    return {
        "start": start,
        "finish": finish,
        "stable": stable,
        "committed_candidate": start["revision"] if committed else None,
        "evidence_kind": "local runtime observation; not trusted CI provenance",
    }


def accept_browser_result(returncode, report):
    if not isinstance(report, dict):
        raise probe.ProbeError("malformed browser report")
    if returncode == 2 and report.get("status") == "BLOCKED":
        raise probe.ToolUnavailable(f"browser unavailable: {report.get('reason')}")
    if returncode != 0 or report.get("status") != "PASS":
        raise probe.ProbeError(f"browser failed (exit {returncode}); inspect webrtc.json")


class WindowsJob:
    """One fixture command and its descendants, including after the driver exits."""

    def __init__(self):
        from ctypes import wintypes as w

        class Limits(ctypes.Structure):
            _fields_ = [
                ("process_time", ctypes.c_longlong),
                ("job_time", ctypes.c_longlong),
                ("flags", w.DWORD),
                ("min_ws", ctypes.c_size_t),
                ("max_ws", ctypes.c_size_t),
                ("active_limit", w.DWORD),
                ("affinity", ctypes.c_size_t),
                ("priority", w.DWORD),
                ("scheduling", w.DWORD),
            ]

        class Extended(ctypes.Structure):
            _fields_ = [
                ("basic", Limits),
                ("io", ctypes.c_ulonglong * 6),
                ("process_memory", ctypes.c_size_t),
                ("job_memory", ctypes.c_size_t),
                ("peak_process_memory", ctypes.c_size_t),
                ("peak_job_memory", ctypes.c_size_t),
            ]

        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.pending_survivors = []
        for name, restype, arguments in [
            ("CreateJobObjectW", w.HANDLE, [ctypes.c_void_p, w.LPCWSTR]),
            ("SetInformationJobObject", w.BOOL, [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]),
            ("AssignProcessToJobObject", w.BOOL, [w.HANDLE, w.HANDLE]),
            (
                "QueryInformationJobObject",
                w.BOOL,
                [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.c_void_p],
            ),
            ("TerminateJobObject", w.BOOL, [w.HANDLE, w.UINT]),
            ("OpenProcess", w.HANDLE, [w.DWORD, w.BOOL, w.DWORD]),
            ("IsProcessInJob", w.BOOL, [w.HANDLE, w.HANDLE, ctypes.POINTER(w.BOOL)]),
            ("WaitForSingleObject", w.DWORD, [w.HANDLE, w.DWORD]),
            ("CloseHandle", w.BOOL, [w.HANDLE]),
        ]:
            function = getattr(self.kernel, name)
            function.restype, function.argtypes = restype, arguments
        self.handle = self.kernel.CreateJobObjectW(None, None)
        self.check(self.handle)
        limits = Extended()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE; no breakaway flags.
        try:
            self.check(
                self.kernel.SetInformationJobObject(
                    self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)
                )
            )
        except BaseException:
            self.close()
            raise

    @staticmethod
    def check(success):
        if not success:
            raise ctypes.WinError(ctypes.get_last_error())

    def assign(self, child):
        self.check(self.kernel.AssignProcessToJobObject(self.handle, int(child._handle)))

    def survivors(self):
        for capacity in (64, 256, 1024, 4096):

            class ProcessIds(ctypes.Structure):
                _fields_ = [
                    ("assigned", ctypes.c_ulong),
                    ("count", ctypes.c_ulong),
                    ("pids", ctypes.c_size_t * capacity),
                ]

            result = ProcessIds()
            success = self.kernel.QueryInformationJobObject(
                self.handle, 3, ctypes.byref(result), ctypes.sizeof(result), None
            )
            if success and result.assigned <= capacity:
                return sorted(set(result.pids[: result.count]) | set(self.pending_survivors))
            if not success and ctypes.get_last_error() != 234:  # ERROR_MORE_DATA
                self.check(False)
        raise probe.ProbeError("fixture job exceeded bounded process inventory")

    def terminate(self):
        from ctypes import wintypes as w

        handles = []
        try:
            for pid in self.survivors():
                # SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION. Membership is rechecked
                # on the handle, so PID reuse cannot extend this job's ownership.
                handle = self.kernel.OpenProcess(0x100000 | 0x1000, False, pid)
                if not handle and ctypes.get_last_error() == 87:  # Already exited.
                    continue
                self.check(handle)
                handles.append((pid, handle))
                belongs = w.BOOL()
                self.check(self.kernel.IsProcessInJob(handle, self.handle, ctypes.byref(belongs)))
                if not belongs.value:
                    handles.pop()
                    self.kernel.CloseHandle(handle)
            self.check(self.kernel.TerminateJobObject(self.handle, 1))
            # Termination is asynchronous. Active-job accounting alone can precede socket
            # teardown; wait on owned process handles as well before reporting cleanup.
            deadline = time.monotonic() + 3
            for pid, handle in handles:
                waited = self.kernel.WaitForSingleObject(
                    handle, max(0, int((deadline - time.monotonic()) * 1000))
                )
                if waited == 258:  # WAIT_TIMEOUT
                    self.pending_survivors.append(pid)
                elif waited != 0:
                    self.check(False)
            if self.pending_survivors:
                raise probe.ProbeError(f"process termination timeout: {self.pending_survivors}")
        finally:
            for _, handle in handles:
                self.kernel.CloseHandle(handle)

    def close(self):
        if self.handle:
            self.check(self.kernel.CloseHandle(self.handle))
            self.handle = None


# The launcher cannot create the tool until the parent assigns its Job Object.
# If the parent dies before assignment, EOF releases the launcher without spawning.
# All other parent-exit paths close the noninherited job handle and kill descendants.
GATED_TOOL = """
import json,pathlib,subprocess,sys
if sys.stdin.buffer.read(1) != b'1':
    sys.exit(125)
report = pathlib.Path(sys.argv[1])
try:
    child = subprocess.Popen(sys.argv[2:], stdin=subprocess.DEVNULL)
    outcome = {'status': 'STARTED', 'pid': child.pid}
except (FileNotFoundError, PermissionError) as error:
    outcome = {'status': 'BLOCKED', 'reason': str(error)}
except OSError as error:
    outcome = {'status': 'FAIL', 'reason': str(error)}
pending = report.with_suffix('.pending')
pending.write_text(json.dumps(outcome), encoding='utf-8')
pending.replace(report)
if outcome['status'] != 'STARTED':
    sys.exit(2 if outcome['status'] == 'BLOCKED' else 1)
sys.exit(child.wait())
"""


class Fixture:
    def __init__(self, output):
        self.output = output
        self.processes = []
        self.commands = []
        self.jobs = {}
        self.cleanup_report = None
        self.http = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def start(self, name, command, env=None):
        if self.cleanup_report is not None:
            raise probe.ProbeError("cannot reuse a closed fixture")
        log = (self.output / f"{name}.log").open("w", encoding="utf-8")
        job = None
        child = None
        try:
            launch_report = self.output / f"{name}-launch.json"
            if os.name == "nt":
                job = WindowsJob()
            argv = (
                [sys.executable, "-B", "-c", GATED_TOOL, str(launch_report), *command]
                if job
                else command
            )
            child = subprocess.Popen(
                argv,
                stdin=subprocess.PIPE if job else subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=HERE,
                env=env,
                start_new_session=os.name != "nt",
            )
            if job:
                job.assign(child)
                self.jobs[child.pid] = job
                child.stdin.write(b"1")
                child.stdin.close()
        except (FileNotFoundError, PermissionError) as error:
            if child:
                child.kill()
                child.wait(timeout=5)
            if job:
                job.close()
            log.close()
            raise probe.ToolUnavailable(f"{name} launch unavailable: {error}") from error
        except BaseException:
            if child:
                child.kill()
                child.wait(timeout=5)
            if job:
                job.close()
            log.close()
            raise
        self.processes.append((name, child, log))
        self.commands.append({"name": name, "pid": child.pid, "argv": command})
        if job:
            deadline = time.monotonic() + 5
            while not launch_report.exists():
                if child.poll() is not None or time.monotonic() >= deadline:
                    raise probe.ProbeError(f"{name} launch acknowledgement missing")
                time.sleep(0.02)
            launch = json.loads(launch_report.read_text(encoding="utf-8"))
            if launch["status"] == "BLOCKED":
                raise probe.ToolUnavailable(f"{name} launch unavailable: {launch['reason']}")
            if launch["status"] != "STARTED":
                raise probe.ProbeError(f"{name} launch failed: {launch['reason']}")
        return child

    def survivors(self, child):
        if os.name == "nt":
            return self.jobs[child.pid].survivors()
        try:
            os.killpg(child.pid, 0)
            return [{"process_group": child.pid}]
        except ProcessLookupError:
            return []

    def stop(self, child):
        if not any(process is child for _, process, _ in self.processes):
            raise probe.ProbeError("process is not owned by this fixture")
        # Job/group membership outlives the direct process; poll() alone is insufficient.
        for sig in (signal.SIGTERM, signal.SIGKILL) if os.name != "nt" else (None,):
            if self.survivors(child):
                if os.name == "nt":
                    self.jobs[child.pid].terminate()
                else:
                    try:
                        os.killpg(child.pid, sig)
                    except ProcessLookupError:
                        pass
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                child.poll()  # Reap our direct child before inspecting its process group.
                if not self.survivors(child):
                    child.wait(timeout=1)
                    return
                time.sleep(0.05)
        raise probe.ProbeError(f"cleanup survivors: {self.survivors(child)}")

    def close(self):
        if self.cleanup_report is not None:
            return self.cleanup_report
        errors = []
        survivors = []
        for name, child, log in reversed(self.processes):
            try:
                self.stop(child)
            except (OSError, subprocess.SubprocessError, probe.ProbeError) as error:
                errors.append(f"{name}: {error}")
            finally:
                try:
                    survivors.extend(
                        {"name": name, "member": member} for member in self.survivors(child)
                    )
                except (OSError, probe.ProbeError) as error:
                    survivors.append({"name": name, "inspection_error": str(error)})
                if os.name == "nt":
                    try:
                        self.jobs[child.pid].close()
                    except OSError as error:
                        errors.append(f"{name} job handle close: {error}")
                log.close()
        self.cleanup_report = {
            "status": "FAIL" if errors or survivors else "PASS",
            "errors": errors,
            "survivors": survivors,
            "ownership": "windows-job-object" if os.name == "nt" else "posix-process-group",
            "processes": [
                {"name": name, "pid": child.pid, "returncode": child.poll()}
                for name, child, _ in self.processes
            ],
        }
        return self.cleanup_report

    def api(self, url):
        with self.http.open(url, timeout=1) as response:
            return json.load(response)

    def observe_outage(self, server, url, started, duration=2):
        # Check immediately and at the end, including when decoding returned very quickly.
        while True:
            if server.poll() is not None:
                raise probe.ProbeError("MediaMTX exited during outage")
            try:
                absent = self.api(url).get("ready") is False
            except urllib.error.HTTPError as error:
                if error.code != 404:
                    raise
                absent = True
            if not absent:
                raise probe.ProbeError("source became ready during the forced outage")
            remaining = duration - (time.monotonic() - started)
            if remaining <= 0:
                return
            time.sleep(min(0.1, remaining))

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
    source_start = source_snapshot()
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
            try:
                version = subprocess.run(
                    [executable, flag], capture_output=True, text=True, timeout=5
                )
            except (FileNotFoundError, PermissionError) as error:
                raise probe.ToolUnavailable(f"{name} prerequisite unavailable: {error}") from error
            if version.returncode or not version.stdout.startswith(expected):
                raise probe.ProbeError(f"expected pinned {name}: {expected}; got {version.stdout}")
            versions[name] = version.stdout.splitlines()[0]
        result["versions"] = versions
        if args.webrtc and not (HERE / "node_modules/playwright/package.json").is_file():
            raise probe.ToolUnavailable(
                "fixture Playwright dependency; run the pinned install first"
            )
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
        before = probe.probe(ffmpeg, rtsp_url, expected_marker="red")
        save(output / "rtsp-before.json", before)
        if before["status"] != "PASS":
            error_type = (
                probe.ToolUnavailable if before["status"] == "BLOCKED" else probe.ProbeError
            )
            raise error_type(f"initial receive: {before.get('reason')}")
        result["before"] = probe.require_frames(before["decoded"], 12)
        result["before"]["marker"] = before["marker"]
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
        fixture.observe_outage(server, path_url, outage_started)
        result["outage"] = {
            "status": "PASS",
            "received_frames": 0,
            "seconds": round(time.monotonic() - outage_started, 3),
        }
        recovery_started = time.monotonic()
        fixture.start("publisher-after", publisher(ffmpeg, rtsp_url, "blue"))
        result["ready_after"] = fixture.wait_path(server, path_url, True)
        after = probe.probe(ffmpeg, rtsp_url, expected_marker="blue")
        save(output / "rtsp-after.json", after)
        if after["status"] != "PASS":
            error_type = probe.ToolUnavailable if after["status"] == "BLOCKED" else probe.ProbeError
            raise error_type(f"recovery receive: {after.get('reason')}")
        result["recovery"] = probe.require_frames(after["decoded"], 12, before["decoded"])
        result["recovery"]["marker"] = after["marker"]
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
            accept_browser_result(browser.returncode, result["webrtc"])
        result["status"] = "PASS"
    except probe.ToolUnavailable as error:
        result.update(status="BLOCKED", reason=str(error))
    except (OSError, subprocess.SubprocessError, ValueError, probe.ProbeError) as error:
        result["reason"] = str(error)
    finally:
        for sock in held:
            sock.close()
        result["cleanup"] = fixture.close()
        if result["cleanup"]["status"] != "PASS":
            result["status"] = "FAIL"
        save(output / "commands.json", fixture.commands)
        result["source"] = source_attribution(source_start, source_snapshot())
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
