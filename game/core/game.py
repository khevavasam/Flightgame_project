"""
core/game.py
============
Core game logic for the flight game.

Defines the `Game` class that manages game state, player actions,
quests, airports, and events.
"""

from __future__ import annotations
from typing import List, Tuple, Optional
from geopy.distance import geodesic
from game.db import AirportRepository
from game.core import Airport, Quest, QuestStatus
from .events.game_event import get_random_events
from game.core.state.game_state import GameState, PlayerState

GAME_NOT_STARTED_ERR: str = "Game not started. call start() first."


class Game:
    """Represents the flight game."""

    START_ICAO = "EFHK"
    COUNTRY = "FI"
    START_FUEL: float = 100.0

    def __init__(self) -> None:
        """Initialize the game instance."""
        self.running: bool = False
        self._airports: List[Airport] = []
        self._last_options: List[Tuple[Airport, float]] = []
        # messages produced by events (weather, etc.)
        self._event_messages: List[str] = []
        self.state: Optional[GameState] = None

    # Quest Helpers
    def _issue_new_quest(self) -> None:
        """Select and assign new active quest for the player."""
        import random

        if not self.state:
            raise RuntimeError(GAME_NOT_STARTED_ERR)

        player_location = self.state.player.location
        candidates = [a for a in self._airports if a.icao != player_location.icao]
        if not candidates:
            self.state.active_quest = None
            self.state.system_msg = ""
            return

        target = random.choice(candidates)
        self.state.active_quest = Quest(target_icao=target.icao)
        self.state.system_msg = f"New quest: Fly to {target.name} ({target.icao})."

    def _get_target_airport(self) -> Optional[Airport]:
        """Return the target Airport object of the active quest."""
        if not self.state or not self.state.active_quest:
            return None
        target_icao = self.state.active_quest.target_icao
        for a in self._airports:
            if a.icao == target_icao:
                return a
        return None

    def _viable_target_option(self, airport: Airport, target: Airport) -> bool:
        """Check if flying to `airport` moves closer to the `target`."""
        distance_to_target = geodesic(
            (airport.lat, airport.lon), (target.lat, target.lon)
        ).km
        remaining_total_distance_to_target = self.remaining_distance_to_target()
        if distance_to_target < remaining_total_distance_to_target:
            return True

        return False

    # Game lifecycle methods
    # ------------------------------------------------------------------------- #
    def start(self) -> None:
        """Start the game, initalize game state and assign first quest."""
        start_airport = AirportRepository.get_by_icao(self.START_ICAO)
        if not start_airport:
            raise RuntimeError("Start airport EFHK not found in DB")

        self._airports = AirportRepository.list_airports(country=self.COUNTRY)
        player = PlayerState(location=start_airport, fuel=self.START_FUEL)
        self.state = GameState(player=player)
        self.running = True
        self._last_options = []
        self._event_messages.clear()

        # Issue the first quest
        self._issue_new_quest()

    def exit_game(self) -> None:
        """Stop the game."""
        self.running = False

    def is_running(self) -> bool:
        """Check if game is running."""
        return self.running

    # Public methods
    # ------------------------------------------------------------------------- #
    def status(self) -> dict:
        """Return current game status as dictionary."""
        if not self.state:
            raise RuntimeError(GAME_NOT_STARTED_ERR)
        s = self.state
        p = s.player
        cur = p.location
        return {
            "icao": cur.icao,
            "name": cur.name,
            "country": cur.country,
            "km_total": int(round(p.km_total)),
            "hops": p.hops,
            "fuel": p.fuel,
            "quest_target": s.active_quest.target_icao if s.active_quest else None,
            "quest_distance": self.remaining_distance_to_target(),
            "points": s.points,
            "system_msg": s.system_msg,
        }

    def options(self, limit: int = 5) -> List[Tuple[Airport, float]]:
        """Return a list of viable airports to fly to with distances in kms."""
        if not self.state:
            raise RuntimeError("Game not started. Call start() first.")

        player_loc = self.state.player.location

        target_airport = self.get_target_airport()
        if target_airport is None:
            raise ValueError("Failed to fetch quest target airport.")

        pairs: List[Tuple[Airport, float]] = []
        for a in self._airports:
            if a.icao == player_loc.icao:
                continue
            if not self._viable_target_option(a, target_airport):
                continue

            dist_km = geodesic((player_loc.lat, player_loc.lon), (a.lat, a.lon)).km
            pairs.append((a, dist_km))

        pairs.sort(key=lambda t: t[1])
        self._last_options = pairs[:limit]
        return self._last_options

    def pick(self, index: int) -> Optional[Airport]:
        """Fly to the chosen airport by `index` and trigger events and handle quests."""
        if not (1 <= index <= len(self._last_options)):
            return None

        if not self.state:
            raise RuntimeError(GAME_NOT_STARTED_ERR)

        chosen, dist = self._last_options[index - 1]
        p = self.state.player

        p.km_total += dist
        p.hops += 1
        p.location = chosen

        self._event_messages.clear()
        events = get_random_events()
        for event in events:
            event.trigger(self)

        # -----Quest check-----
        if (
            self.state.active_quest
            and chosen.icao == self.state.active_quest.target_icao
        ):
            # complete current quest
            self.state.active_quest.status = QuestStatus.COMPLETED
            finished = self.state.active_quest
            self.state.completed_quests.append(finished)
            self.state.points += 1

            # issue a new one
            self._issue_new_quest()
            if self.state.active_quest:
                self.state.system_msg = (
                    f"Quest completed: {finished.target_icao}! +1 point. "
                    f"Next target: {self.state.active_quest.target_icao}."
                )
            else:
                self.state.system_msg = (
                    f"Quest completed: {finished.target_icao}! +1 point."
                )
        else:
            # no quest-related event this hop
            if not self.state.system_msg.startswith("New quest"):
                self.state.system_msg = ""

        return chosen

    def get_airports(self) -> List[Airport]:
        """Return all loaded airports."""
        return self._airports

    def get_target_airport(self) -> Optional[Airport]:
        """Return the target airport of active quest."""
        return self._get_target_airport()

    def remaining_distance_to_target(self) -> Optional[int]:
        """Remaining distance to the target airport (rounded km)."""
        if not self.state or not self.state.player or not self.state.active_quest:
            return None

        player_location = self.state.player.location
        target = self._get_target_airport()
        if not target:
            return None

        dist_km = geodesic(
            (player_location.lat, player_location.lon), (target.lat, target.lon)
        ).km
        return int(round(dist_km))

    def add_event_message(self, msg: str) -> None:
        """Append messages produced by game events to the queue."""
        self._event_messages.append(msg)
