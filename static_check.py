import subprocess
import sys

for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        _reconfigure(encoding="utf-8", errors="replace")

root = __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0] or "."


subprocess.check_call([sys.executable, "-m", "compileall", "-q", "pyusd"], cwd=root)
subprocess.check_call([sys.executable, "-m", "ruff", "check", "--fix", "--unsafe-fixes", "."], cwd=root)
subprocess.check_call([sys.executable, "-m", "ty", "check", "."], cwd=root)
