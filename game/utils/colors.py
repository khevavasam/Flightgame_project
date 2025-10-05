"""
utils/colors.py
===============
ANSI color utilities for cli/terminal output.

Uses `colorama` for crossplatform compatibility.
Colors disabled if `NO_COLOR` set or output is not a terminal (tty).
"""

import os
import sys
from colorama import init

init()
ENABLE_COLOR = sys.stdout.isatty() and not os.getenv("NO_COLOR")


def _c(code: str, s: str) -> str:
    """Wrap string `s` with ANSI color code `code`"""
    return f"\x1b[{code}m{s}\x1b[0m" if ENABLE_COLOR else s


def ok(s):
    """Bold green text."""
    return _c("1;32", s)


def warn(s):
    """Bold yellow text."""
    return _c("1;33", s)


def err(s):
    """Bold red text."""
    return _c("1;31", s)


def info(s):
    """Bold cyan text."""
    return _c("1;36", s)


def dim(s):
    """Dimmed text."""
    return _c("2", s)


def bold(s):
    """Bold text."""
    return _c("1", s)
