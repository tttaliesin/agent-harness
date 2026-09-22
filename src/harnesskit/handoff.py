"""Write a resumable reference without copying conversation or claiming durable upload."""

from . import config
from .common import atomic_write
from .evidence import inspect


def handoff(root, git, change_id, base, evidence_path, next_command, durable=None, locks=None):
    result = inspect(root, git, [change_id], base, evidence_path, locks)
    product = config.project(root)
    change = config.change(root, change_id, product["documents"]["specs"])
    refs = durable or []
    lines = [
        f"# Handoff: {change_id}",
        "",
        f"Verification status: {result['status']}",
        "",
        f"Candidate: {git.call('rev-parse', 'HEAD').strip()}",
        f"Base: {base}",
        "",
        f"Local evidence: {evidence_path}",
        "",
        "Durable references (caller supplied; availability not verified):",
        "",
    ]
    lines += (
        [f"- {ref}" for ref in refs]
        if refs
        else ["None; preserve this worktree until evidence is exported."]
    )
    lines += [
        "",
        "Specification references:",
        "",
        *[f"- {ref}" for ref in change["spec_refs"]],
        "",
        "Next command:",
        "",
        "```text",
        next_command.replace("```", ""),
        "```",
        "",
        "Commit changes to this handoff before refreshing candidate verification and reviews.",
        "",
    ]
    path = f"{product['documents']['specs']}/changes/{change_id}/handoff.md"
    atomic_write(root, path, "\n".join(lines))
    return {
        "status": result["status"],
        "handoff": path,
        "evidence": result,
        "durable_verified": False,
        "candidate_refresh_required": True,
    }
