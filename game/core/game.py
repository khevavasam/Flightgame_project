from __future__ import annotations
from typing import List, Tuple, Optional
from geopy.distance import geodesic
from game.db import AirportRepository
from game.core import Airport
from .events.game_event import get_random_events
from .quest import Quest, QuestStatus


class Game:
    START_ICAO = "EFHK"
    COUNTRY = "FI"
    START_FUEL: float = 100.0

    def __init__(self) -> None:
        self.running: bool = True
        self.current: Optional[Airport] = None
        self.km_total: float = 0.0
        self.hops: int = 0
        self.resources = {"fuel": 0.0}
        self._airports: List[Airport] = []
        self._last_options: List[Tuple[Airport, float]] = []

        # messages produced by events (weather, etc.)
        self._event_messages: List[str] = []

        # Quests
        self.quest_active: Optional[Quest] = None
        self.quest_completed: List[Quest] = []
        self.points: int = 0
        self._system_msg: str = ""

    def start(self) -> None:
        self.current = AirportRepository.get_by_icao(self.START_ICAO)
        if not self.current:
            raise RuntimeError("Start airport EFHK not found in DB")
        self._airports = AirportRepository.list_airports(country=self.COUNTRY)
        self.km_total = 0.0
        self.hops = 0
        self.resources["fuel"] = self.START_FUEL
        self._last_options = []
        self._event_messages.clear()

        # Issue the first quest
        self._issue_new_quest()

    def status(self) -> dict:
        cur = self.current
        return {
            "icao": cur.icao if cur else None,
            "name": cur.name if cur else None,
            "country": cur.country if cur else None,
            "km_total": int(round(self.km_total)),
            "hops": self.hops,
            "fuel": self.resources["fuel"],
            # quest-related
            "quest_target": self.quest_active.target_icao
            if self.quest_active
            else None,
            "quest_distance": self.remaining_distance_to_target(),
            "points": self.points,
            "system_msg": self._system_msg,
        }

    def options(self, limit: int = 5) -> List[Tuple[Airport, float]]:
        assert self.current is not None, "Game not started. Call start()."
        cur = self.current
        pairs: List[Tuple[Airport, float]] = []
        for a in self._airports:
            if a.icao == cur.icao:
                continue
            # geodesic returns an object with .km
            dist_km = geodesic((cur.lat, cur.lon), (a.lat, a.lon)).km
            pairs.append((a, dist_km))
        pairs.sort(key=lambda t: t[1])
        self._last_options = pairs[:limit]
        return self._last_options

    def pick(self, index: int) -> Optional[Airport]:
        if not (1 <= index <= len(self._last_options)):
            return None
        chosen, dist = self._last_options[index - 1]
        self.km_total += dist
        self.hops += 1
        self.current = chosen

        self._event_messages.clear()
        events = get_random_events()
        for event in events:
            event.trigger(self)

        # -----Quest check-----
        if self.quest_active and self.current.icao == self.quest_active.target_icao:
            # complete current quest
            self.quest_active.status = QuestStatus.COMPLETED
            finished = self.quest_active
            self.quest_completed.append(finished)
            self.points += 1

            # issue a new one
            self._issue_new_quest()
            if self.quest_active:
                self._system_msg = (
                    f"Quest completed: {finished.target_icao}! +1 point. "
                    f"Next target: {self.quest_active.target_icao}."
                )
            else:
                self._system_msg = f"Quest completed: {finished.target_icao}! +1 point."
        else:
            # no quest-related event this hop
            if not self._system_msg.startswith("New quest"):
                self._system_msg = ""

        return chosen

    def exit_game(self) -> None:
        self.running = False

    def is_running(self) -> bool:
        return self.running

    # Quest Helpers
    def _issue_new_quest(self) -> None:
        import random

        assert self.current is not None, "Game not started. Call start()."

        candidates = [a for a in self._airports if a.icao != self.current.icao]
        if not candidates:
            self.quest_active = None
            self._system_msg = ""
            return

        target = random.choice(candidates)
        self.quest_active = Quest(target_icao=target.icao)
        self._system_msg = f"New quest: Fly to {target.name} ({target.icao})."

    def _get_target_airport(self) -> Optional[Airport]:
        if not self.quest_active:
            return None
        for a in self._airports:
            if a.icao == self.quest_active.target_icao:
                return a
        return None

    def get_target_airport(self) -> Optional[Airport]:
        return self._get_target_airport()

    def remaining_distance_to_target(self) -> Optional[int]:
        """Remaining distance to the target airport (rounded km)."""
        if not (self.current and self.quest_active):
            return None
        target = self._get_target_airport()
        if not target:
            return None
        dist_km = geodesic(
            (self.current.lat, self.current.lon), (target.lat, target.lon)
        ).km
        return int(round(dist_km))

    # Messaging for events
    def add_event_message(self, msg: str) -> None:
        self._event_messages.append(msg)
