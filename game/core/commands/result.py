"""
core/commands/result.py
=======================
Defines the result and status types for the game commands.

Includes `CommandStatus` enum (ok,error) and CommandResult class
to encapsulate messages and execution status.
"""

from dataclasses import dataclass
from typing import List
from enum import Enum


class CommandStatus(Enum):
    """Status of a command execution."""

    OK = "ok"
    ERROR = "error"


@dataclass
class CommandResult:
    """Encapsulates messages and status returned by a command."""

    messages: List[str]
    status: CommandStatus = CommandStatus.OK
