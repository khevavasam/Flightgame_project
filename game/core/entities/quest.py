"""
core/entities/quest.py
======================
Defines a quest/mission for the game.

Includes `QuestStatus` enum and `Quest` class for active and completed quests
in the game.
"""

from dataclasses import dataclass
from enum import Enum


class QuestStatus(Enum):
    """Completion status of the quest."""

    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


@dataclass
class Quest:
    """Represents a game quest with objectives."""

    target_icao: str
    status: QuestStatus = QuestStatus.ACTIVE
