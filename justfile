set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

default:
    @just --list

# Inspect selected tools without installing dependencies.
doctor:
    python scripts/dev.py doctor

# Explicit dependency installation from the reviewed lock.
sync:
    python scripts/dev.py sync

# Maintainer source checks and behavioral tests; no consumer runtime build.
check:
    python scripts/dev.py check

test:
    python scripts/dev.py test

# Deliberately edits source formatting; never called by check.
format:
    python scripts/dev.py format
