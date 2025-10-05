"""
core/state/state.py
===================
Defines the player and game state data structures.

Includes `PlayerState` for current location, fuel, hops, and distance,
and `GameState` for overall game progress, quests, points, and system messages.
"""

from dataclasses import dataclass, asdict, field
from typing import List, Optional
from game.core.entities.airport import Airport
from game.core.entities.quest import Quest


@dataclass
class PlayerState:
    """Represents the current state of the player."""

    location: Airport
    fuel: float = 100.0
    hops: int = 0
    km_total: float = 0.0


@dataclass
class GameState:
    """Represents the overall state of the game."""

    player: PlayerState
    active_quest: Optional[Quest] = None
    completed_quests: List[Quest] = field(default_factory=list)
    points: int = 0
    system_msg: str = ""

    def to_dict(self) -> dict:
        """Return the game state as dictionary."""
        return asdict(self)
