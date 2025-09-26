import os, sys
from colorama import init

init()
ENABLE_COLOR = sys.stdout.isatty() and not os.getenv("NO_COLOR")

def _c(code: str, s: str) -> str:
    return f"\x1b[{code}m{s}\x1b[0m" if ENABLE_COLOR else s

def ok(s):   return _c("1;32", s)   # bold green
def warn(s): return _c("1;33", s)   # bold yellow
def err(s):  return _c("1;31", s)   # bold red
def info(s): return _c("1;36", s)   # bold cyan
def dim(s):  return _c("2", s)      # dim
def bold(s): return _c("1", s)      # bold
