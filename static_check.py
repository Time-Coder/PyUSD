import subprocess
import sys

for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        _reconfigure(encoding="utf-8", errors="replace")

root = __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0] or "."


# Only pyusd is compiled here. The math types are a separate project one
# directory up, with their own static_check.py; ruff and ty still walk the whole
# tree below, which is what catches anything this repository imports from it.
subprocess.check_call([sys.executable, "-m", "compileall", "-q", "pyusd"], cwd=root)

subprocess.check_call([sys.executable, "-m", "ruff", "check", "--fix", "--unsafe-fixes", "."], cwd=root)
subprocess.check_call([sys.executable, "-m", "ty", "check", "."], cwd=root)
