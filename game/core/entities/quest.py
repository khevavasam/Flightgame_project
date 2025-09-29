from dataclasses import dataclass
from enum import Enum


class QuestStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


@dataclass
class Quest:
    target_icao: str
    status: QuestStatus = QuestStatus.ACTIVE
