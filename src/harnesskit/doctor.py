"""Read-only diagnostics: tools and files, with unimplemented trust interfaces explicit."""

import sys

from . import __version__, binding, config
from .common import HarnessError, aggregate
from .process import executable


def doctor(root, git):
    product = config.project(root)
    checks = []
    for name, definition in product["verification"]["checks"].items():
        try:
            path = executable(definition["command"])
            checks.append({"id": name, "status": "PASS", "executable": path})
        except HarnessError as exc:
            checks.append({"id": name, **exc.result})
    drift = binding.check(root)
    return {
        "status": aggregate([drift["status"], *[c["status"] for c in checks]]),
        "version": __version__,
        "python": sys.version,
        "git": git.call("--version").strip(),
        "tools": checks,
        "binding": drift,
        "interfaces": {
            "ci_provenance": "BLOCKED",
            "readonly_enforcement": "BLOCKED",
            "desktop_live_acceptance": "NOT_RUN",
            "followup_schedule": "NOT_CONFIGURED",
        },
    }
