from dataclasses import dataclass
from typing import List
from enum import Enum


class CommandStatus(Enum):
    OK = "ok"
    ERROR = "error"


@dataclass
class CommandResult:
    messages: List[str]
    status: CommandStatus = CommandStatus.OK
