from dataclasses import dataclass, asdict, field
from typing import List, Optional
from game.core.quest import Quest
from game.core.entities.airport import Airport


@dataclass
class PlayerState:
    location: Airport
    fuel: float = 100.0
    hops: int = 0
    km_total: float = 0.0


@dataclass
class GameState:
    player: PlayerState
    active_quest: Optional[Quest] = None
    completed_quests: List[Quest] = field(default_factory=list)
    points: int = 0
    system_msg: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
