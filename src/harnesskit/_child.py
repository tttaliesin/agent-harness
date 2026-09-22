"""Internal launch gate: do not spawn descendants before the Windows Job is attached."""

import subprocess
import sys

if sys.stdin.buffer.read(1) != b"1":
    raise SystemExit(125)
raise SystemExit(subprocess.call(sys.argv[1:], stdin=subprocess.DEVNULL, shell=False))
