"""HTTP contracts exercised against an owned service process on a dynamic port."""

import json
import queue
import subprocess
import sys
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.fixture(scope="module")
def service():
    with subprocess.Popen(
        [sys.executable, "-B", str(APP), "--port", "0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as process:
        ready = queue.Queue()
        reader = threading.Thread(target=lambda: ready.put(process.stdout.readline()), daemon=True)
        reader.start()
        try:
            line = ready.get(timeout=10)
            assert line, "service exited before reporting its address"
            yield json.loads(line)["url"]
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            reader.join(timeout=2)


def request(service, path, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = urlopen(Request(service + path, headers=headers), timeout=5)
    except HTTPError as error:
        response = error
    with response:
        return response.status, json.loads(response.read())


def test_health_identifies_the_fixture(service):
    assert request(service, "/health") == (200, {"service": "agent-harness-web-api", "ready": True})


def test_greeting_preserves_valid_input(service):
    assert request(service, "/api/greet?name=Ada") == (200, {"message": "Hello, Ada!"})


@pytest.mark.parametrize("query", ["", "?name=", "?name=%20%20", "?name=" + "x" * 41])
def test_invalid_input_returns_validation_error(service, query):
    assert request(service, "/api/greet" + query) == (
        422,
        {"error": "Name must contain 1 to 40 characters"},
    )


@pytest.mark.parametrize("token", [None, "invalid-public-fixture-token"])
def test_missing_or_invalid_identity_is_unauthorized(service, token):
    assert request(service, "/api/admin", token) == (401, {"error": "Authentication required"})


def test_viewer_cannot_access_admin_action(service):
    assert request(service, "/api/admin", "public-fixture-viewer") == (
        403,
        {"error": "Admin role required"},
    )


def test_admin_can_access_admin_action(service):
    assert request(service, "/api/admin", "public-fixture-admin") == (
        200,
        {"message": "Admin access granted"},
    )


def test_expected_service_failure_is_observable_and_recovery_is_real(service):
    assert request(service, "/api/error") == (503, {"error": "Fixture service unavailable"})
    assert request(service, "/api/greet?name=Recovered") == (
        200,
        {"message": "Hello, Recovered!"},
    )


def test_unknown_route_is_not_success(service):
    assert request(service, "/api/missing") == (404, {"error": "Not found"})
