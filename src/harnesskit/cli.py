"""Command line protocol: JSON results, 0 PASS / 1 FAIL / 2 BLOCKED."""

import argparse
import json
import sys
from pathlib import Path

from . import (
    binding,
    config,
    doctor,
    evidence,
    followup,
    handoff,
    hooks,
    review,
    verification,
    workspace,
)
from .common import EXITS, HarnessError, read_json, safe_path, unique_pairs
from .git import Git


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise HarnessError("invalid_arguments", detail=message)


def parser():
    result = Parser(prog="harnesskit", description=__doc__)
    result.add_argument("--root", default=".")
    result.add_argument("--git", default="git", help="Native Git executable")
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("doctor", "check"):
        command = commands.add_parser(name)
        if name == "check":
            command.add_argument("--change", action="append")
    sync = commands.add_parser("sync")
    sync.add_argument("--template-root", required=True)
    sync.add_argument("--manifest", required=True)
    sync.add_argument("--lock", default="harness/lock.json")
    for name in ("verify", "evidence", "review", "handoff"):
        command = commands.add_parser(name)
        command.add_argument("--change", action="append", required=True)
        command.add_argument("--base", required=True, help="Immutable trusted baseline commit SHA")
        command.add_argument("--lock", action="append", help="Additional fingerprinted lock path")
        if name in {"verify", "review"}:
            command.add_argument("--local", action="store_true")
        if name == "evidence":
            command.add_argument("--file", required=True)
            command.add_argument("--require-ci", action="store_true")
        if name in {"review", "handoff"}:
            command.add_argument("--evidence", required=True)
        if name == "review":
            command.add_argument("--spec", required=True)
            command.add_argument("--standards", required=True)
        if name == "handoff":
            command.add_argument("--next", required=True)
            command.add_argument("--durable", action="append")
    for name in ("lease", "clean"):
        command = commands.add_parser(name)
        if name == "lease":
            command.add_argument("action", choices=["acquire", "release"])
            command.add_argument("--resource")
            command.add_argument("--ttl", type=int, default=3600)
        command.add_argument("--change", required=True)
        command.add_argument("--owner", required=True)
        command.add_argument("--registry", required=True)
        command.add_argument("--token")
    hook = commands.add_parser("hook")
    hook.add_argument("--input", required=True, help="Relative JSON path, or - for stdin")
    follow = commands.add_parser("followup")
    follow.add_argument("--input", required=True)
    follow.add_argument("--registry", required=True)
    follow.add_argument("--complete", action="store_true")
    follow.add_argument("--token")
    return result


def input_json(root, path):
    if path != "-":
        return read_json(safe_path(root, path, must_exist=True))
    content = sys.stdin.read(65537)
    if len(content) > 65536:
        raise HarnessError("event_input_too_large")
    try:
        return json.loads(content, object_pairs_hook=unique_pairs)
    except ValueError as exc:
        raise HarnessError("invalid_event_json", detail=str(exc)) from exc


def dispatch(args, root):
    if args.command == "sync":
        return binding.sync(root, Path(args.template_root), args.manifest, args.lock)
    if args.command == "hook":
        event = input_json(root, args.input)
        maximum = config.project(root)["workflow"]["maximum_repair_rounds"]
        return hooks.handle(root, event, maximum)
    git = Git(root, args.git)
    if args.command == "doctor":
        return doctor.doctor(root, git)
    if args.command == "check":
        product = config.project(root)
        if args.change:
            config.select(root, product, args.change)
        return binding.check(root)
    if args.command in {"lease", "clean"}:
        product = config.project(root)
        config.change(root, args.change, product["documents"]["specs"])
        if args.command == "lease" and args.action == "acquire":
            if not args.resource:
                raise HarnessError("lease_resource_required")
            return workspace.acquire(
                root,
                args.registry,
                product["project"]["id"],
                args.change,
                args.owner,
                args.resource,
                args.ttl,
            )
        if not args.token:
            raise HarnessError("lease_token_required")
        return workspace.release(
            root, args.registry, args.change, args.owner, args.token, clean=args.command == "clean"
        )
    if args.command == "followup":
        return followup.handle(
            root, git, input_json(root, args.input), args.registry, args.complete, args.token
        )
    locks = sorted(set(["harness/lock.json", *(args.lock or [])]))
    if args.command == "verify":
        return verification.verify(root, git, args.change, args.base, locks, args.local)
    if args.command == "evidence":
        return evidence.inspect(
            root, git, args.change, args.base, args.file, locks, args.require_ci
        )
    if args.command == "review":
        return review.review(
            root,
            git,
            args.change,
            args.base,
            args.evidence,
            args.spec,
            args.standards,
            locks,
            args.local,
        )
    if len(args.change) != 1:
        raise HarnessError("handoff_requires_one_change")
    return handoff.handoff(
        root, git, args.change[0], args.base, args.evidence, args.next, args.durable, locks
    )


def main(argv=None):
    native_hook = False
    try:
        args = parser().parse_args(argv)
        root = Path(args.root).resolve(strict=True)
        if args.command == "hook":
            # Read once (stdin cannot be replayed), keep native errors off its decision channel.
            event = input_json(root, args.input)
            native_hook = isinstance(event, dict) and event.get("adapter") == "codex-desktop"
            maximum = config.project(root)["workflow"]["maximum_repair_rounds"]
            result = hooks.handle(root, event, maximum)
        else:
            result = dispatch(args, root)
    except HarnessError as exc:
        result = exc.result
    except (OSError, UnicodeError) as exc:
        result = {"status": "BLOCKED", "reason": "io_unavailable", "detail": str(exc)}
    except KeyboardInterrupt:
        result = {"status": "BLOCKED", "reason": "interrupted"}
    if native_hook:
        if "status" in result:
            print(json.dumps(result, sort_keys=True), file=sys.stderr)
            result = {
                "systemMessage": "Harness hook could not complete; no continuation requested."
            }
        print(json.dumps(result, sort_keys=True))
        return 0  # Native exit 2 would request continuation on Stop/SubagentStop.
    print(json.dumps(result, sort_keys=True))
    return EXITS.get(result.get("status"), 2)
