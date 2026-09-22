"""Bounded argv runner with process-group / Windows Job Object lifetime ownership."""

import ctypes
import os
import shutil
import signal
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from .common import HarnessError, blocked, digest, safe_path


def now():
    return datetime.now(UTC).isoformat()


class WindowsJob:
    def __init__(self):
        from ctypes import wintypes as w

        class Basic(ctypes.Structure):
            _fields_ = [
                ("process_time", ctypes.c_int64),
                ("job_time", ctypes.c_int64),
                ("flags", w.DWORD),
                ("min_ws", ctypes.c_size_t),
                ("max_ws", ctypes.c_size_t),
                ("active", w.DWORD),
                ("affinity", ctypes.c_size_t),
                ("priority", w.DWORD),
                ("scheduling", w.DWORD),
            ]

        class IO(ctypes.Structure):
            _fields_ = [
                (name, ctypes.c_uint64)
                for name in ("read_ops", "write_ops", "other_ops", "read", "write", "other")
            ]

        class Extended(ctypes.Structure):
            _fields_ = [
                ("basic", Basic),
                ("io", IO),
                ("process_memory", ctypes.c_size_t),
                ("job_memory", ctypes.c_size_t),
                ("peak_process", ctypes.c_size_t),
                ("peak_job", ctypes.c_size_t),
            ]

        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        self.api.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
        self.api.CreateJobObjectW.restype = w.HANDLE
        self.api.SetInformationJobObject.argtypes = [
            w.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            w.DWORD,
        ]
        self.api.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
        self.api.TerminateJobObject.argtypes = [w.HANDLE, w.UINT]
        self.api.CloseHandle.argtypes = [w.HANDLE]
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            blocked("windows_job_unavailable")
        limits = Extended()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.api.SetInformationJobObject(
            self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)
        ):
            self.api.CloseHandle(self.handle)
            blocked("windows_job_limits_unavailable")

    def attach(self, process):
        if not self.api.AssignProcessToJobObject(self.handle, int(process._handle)):
            blocked("windows_job_assignment_denied")

    def close(self):
        killed = self.api.TerminateJobObject(self.handle, 124)
        closed = self.api.CloseHandle(self.handle)
        return bool(killed and closed)


def executable(command):
    if (
        not isinstance(command, list)
        or not command
        or any(not isinstance(arg, str) or not arg or "\x00" in arg for arg in command)
    ):
        raise HarnessError("invalid_argv")
    path = shutil.which(command[0])
    if not path:
        blocked("tool_missing", tool=command[0])
    if os.name == "nt" and Path(path).suffix.lower() in {".bat", ".cmd"}:
        blocked("implicit_windows_shell_forbidden", tool=command[0])
    return path


def run(root, command, timeout, run_dir, check_id, env=None):
    if timeout <= 0 or timeout > 86400:
        raise HarnessError("invalid_timeout")
    stdout = f"{run_dir}/{check_id}.stdout.log"
    stderr = f"{run_dir}/{check_id}.stderr.log"
    out = safe_path(root, stdout)
    err = safe_path(root, stderr)
    out.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "id": check_id,
        "argv": command,
        "cwd": str(Path(root).resolve()),
        "started": now(),
        "exit_code": None,
        "timed_out": False,
        "cleanup": "not_started",
        "status": "BLOCKED",
    }
    process = None
    job = None
    with out.open("xb") as out_stream, err.open("xb") as err_stream:
        try:
            binary = executable(command)
            argv = [binary, *command[1:]]
            if os.name == "nt":
                job = WindowsJob()
                argv = [sys.executable, str(Path(__file__).with_name("_child.py")), *argv]
            process = subprocess.Popen(
                argv,
                cwd=root,
                env=env,
                shell=False,
                stdin=subprocess.PIPE,
                stdout=out_stream,
                stderr=err_stream,
                start_new_session=os.name != "nt",
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            if job:
                job.attach(process)
                process.stdin.write(b"1")
                process.stdin.flush()
            process.stdin.close()
            try:
                result["exit_code"] = process.wait(timeout=timeout)
                result["status"] = "PASS" if process.returncode == 0 else "FAIL"
                if process.returncode:
                    result["reason"] = "nonzero_exit"
            except subprocess.TimeoutExpired:
                result.update(status="FAIL", reason="timeout", timed_out=True)
        except HarnessError as exc:
            result.update(exc.result)
            # Runner records only fields belonging to its evidence schema.
            result.pop("tool", None)
        except OSError as exc:
            result.update(status="BLOCKED", reason=f"process_unavailable: {exc}")
        finally:
            if process:
                if job:
                    cleaned = job.close()
                    job = None
                    if process.poll() is None:
                        process.kill()  # Also covers a denied Job assignment before the gate.
                else:
                    cleaned = True
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    except OSError:
                        cleaned = False
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    cleaned = False
                result["cleanup"] = "complete" if cleaned else "failed"
                if not cleaned:
                    result.update(status="BLOCKED", reason="child_cleanup_unconfirmed")
            if job:
                job.close()
    result["finished"] = now()
    result["stdout"] = {"path": stdout, "sha256": digest(out.read_bytes())}
    result["stderr"] = {"path": stderr, "sha256": digest(err.read_bytes())}
    return result
