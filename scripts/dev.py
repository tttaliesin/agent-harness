"""Repository task entry points; native argv, selected Python, no implicit installs."""

import os
import shutil
import subprocess
import sys
import tomllib
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(argv, env):
    print("+ " + " ".join(argv), flush=True)
    subprocess.run(argv, cwd=ROOT, env=env, check=True)


def main():
    action = sys.argv[1] if len(sys.argv) == 2 else "doctor"
    if action not in {"doctor", "sync", "check", "test", "build", "format"}:
        raise SystemExit("Unknown task")
    selected = tomllib.loads((ROOT / "mise.toml").read_text())["tools"]
    actual_python = ".".join(str(value) for value in sys.version_info[:3])
    if actual_python != selected["python"]:
        raise SystemExit(f"Select Python {selected['python']}; observed {actual_python}")
    uv = shutil.which("uv")
    if not uv:
        raise SystemExit("uv is missing; explicitly install the version in mise.toml")
    actual_uv = subprocess.check_output([uv, "--version"], text=True).split()[1]
    if actual_uv != selected["uv"]:
        raise SystemExit(f"Select uv {selected['uv']}; observed {actual_uv}")
    env = dict(os.environ, UV_PYTHON=sys.executable, UV_PYTHON_DOWNLOADS="never")
    if action == "doctor":
        print(f"Python {actual_python}: {sys.executable}\nuv {actual_uv}: {uv}")
        return
    run([uv, "lock", "--check"], env)
    if action == "sync":
        run([uv, "sync", "--locked", "--python", sys.executable], env)
        return
    prefix = [uv, "run", "--no-sync"]
    if action == "format":
        run(prefix + ["ruff", "format", "src", "scripts", "tests"], env)
        return
    if action == "check":
        run(prefix + ["ruff", "check", "src", "scripts", "tests"], env)
        run(prefix + ["python", "scripts/check-packages.py"], env)
        run(prefix + ["python", "scripts/check-templates.py"], env)
    if action in {"check", "test"}:
        report = ".harness/development/reports/pytest.xml"
        (ROOT / report).parent.mkdir(parents=True, exist_ok=True)
        # Keep native Windows test paths below MAX_PATH without changing host policy.
        temporary = f".harness/t-{uuid.uuid4().hex[:12]}"
        if (ROOT / temporary).exists():
            raise SystemExit("Test directory collision; rerun to select a fresh path")
        run(prefix + ["pytest", "-q", f"--basetemp={temporary}", f"--junitxml={report}"], env)
    if action in {"check", "build"}:
        run(prefix + ["python", "-m", "build", "--no-isolation"], env)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc
