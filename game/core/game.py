from __future__ import annotations
from typing import List, Tuple, Optional
from geopy.distance import geodesic
from game.db import AirportRepository
from game.core import Airport, Quest, QuestStatus
from .events.game_event import get_random_events
from game.core.state.game_state import GameState, PlayerState
from game.utils.colors import ok, warn, err, info, dim, bold
from .planning import compute_player_rule_route, RouteResult

GAME_NOT_STARTED_ERR: str = "Game not started. call start() first."


class Game:
    START_ICAO = "EFHK"
    COUNTRY = "FI"
    START_FUEL: float = 100.0
    FUEL_PER_KM: float = 0.08
    FUEL_TAKEOFF_LANDING: float = 2.0

    def __init__(self) -> None:
        self.running: bool = False
        self._airports: List[Airport] = []
        self._last_options: List[Tuple[Airport, float]] = []
        # messages produced by events (weather, etc.)
        self._event_messages: List[str] = []
        self.state: Optional[GameState] = None
        self._fuel_factor: float = 1.0
        self._fuel_fixed: float = 0.0

        self._ideal_route: Optional[RouteResult] = None
        self._quest_actual_base_fuel: float = 0.0
        self._quest_actual_fuel: float = 0.0
        self._quest_start_km_total: float = 0.0
        self._quest_start_hops: int = 0

    # Quest Helpers
    def _issue_new_quest(self) -> None:
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

        self._ideal_route = compute_player_rule_route(
            start_airport=player_location,
            target_airport=target,
            all_airports=self._airports,
            fuel_per_km=self.FUEL_PER_KM,
            fuel_fixed=self.FUEL_TAKEOFF_LANDING,
            k_neighbors=5,
        )
        self._quest_actual_base_fuel = 0.0
        self._quest_actual_fuel = 0.0
        self._quest_start_km_total = self.state.player.km_total
        self._quest_start_hops = self.state.player.hops

    def _get_target_airport(self) -> Optional[Airport]:
        if not self.state or not self.state.active_quest:
            return None
        target_icao = self.state.active_quest.target_icao
        for a in self._airports:
            if a.icao == target_icao:
                return a
        return None

    def _viable_target_option(self, airport: Airport, target: Airport) -> bool:
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
        start_airport = AirportRepository.get_by_icao(self.START_ICAO)
        if not start_airport:
            raise RuntimeError("Start airport EFHK not found in DB")

        self._airports = AirportRepository.list_airports(country=self.COUNTRY)
        player = PlayerState(location=start_airport, fuel=self.START_FUEL)
        self.state = GameState(player=player)
        self.running = True
        self._last_options = []
        self._event_messages.clear()
        self._fuel_factor = 1.0
        self._fuel_fixed = 0.0

        self._ideal_route = None
        self._quest_actual_base_fuel = 0.0
        self._quest_actual_fuel = 0.0
        self._quest_start_km_total = 0.0
        self._quest_start_hops = 0

        # Issue the first quest
        self._issue_new_quest()

    def exit_game(self) -> None:
        self.running = False

    def is_running(self) -> bool:
        return self.running

    # Public methods
    # ------------------------------------------------------------------------- #
    def status(self) -> dict:
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
    def _consume_fuel_for_leg(self, dist_km: float) -> float:
        if not self.state:
            raise RuntimeError(GAME_NOT_STARTED_ERR)

        base = self.FUEL_TAKEOFF_LANDING + self.FUEL_PER_KM * dist_km
        burn = (base + self._fuel_fixed) * self._fuel_factor

        p = self.state.player
        p.fuel = max(0.0, p.fuel - burn)

        self._quest_actual_fuel += burn

        status_color = err if p.fuel <= 0 else (warn if p.fuel <= 8.0 else ok)
        msg = f"⛽  Fuel used: {err(f'{burn:.1f} L')} | Remaining: {status_color(f'{p.fuel:.1f} L')}"
        self._event_messages.append(msg)

        self._fuel_factor = 1.0
        self._fuel_fixed = 0.0
        return burn

    def options(self, limit: int = 5) -> List[Tuple[Airport, float]]:
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

        base_burn = self.FUEL_TAKEOFF_LANDING + self.FUEL_PER_KM * dist
        self._quest_actual_base_fuel += base_burn

        self._consume_fuel_for_leg(dist)

        if p.fuel <= 0:
            self.state.system_msg = "Out of fuel!"
            self.running = False
            return chosen

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

            p.fuel = self.START_FUEL

            # --- begin colored report block ---
            if self._ideal_route and self._ideal_route.success:
                ideal_fuel = self._ideal_route.base_fuel
                ideal_dist = self._ideal_route.distance_km
                ideal_hops = self._ideal_route.hops
            else:
                # fallback
                actual_dist = p.km_total - self._quest_start_km_total
                actual_hops = p.hops - self._quest_start_hops
                ideal_dist = actual_dist
                ideal_hops = actual_hops
                ideal_fuel = self._quest_actual_base_fuel

            actual_base = max(0.0, self._quest_actual_base_fuel)
            actual_real = max(0.0, self._quest_actual_fuel)
            weather_penalty = max(0.0, actual_real - actual_base)

            actual_dist = p.km_total - self._quest_start_km_total
            actual_hops = p.hops - self._quest_start_hops

            if actual_base > 0:
                eff = ideal_fuel / actual_base
                score = int(round(100 * (eff ** 1.1)))
            else:
                score = 100
            score = max(0, min(100, score))
            grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "E"

            # local color pickers
            def _score_fx(s: int):
                if s >= 90: return ok
                if s >= 75: return info
                if s >= 60: return warn
                return err

            def _penalty_fx(pen_l: float):
                if pen_l <= 0.5:  return ok
                if pen_l <= 5.0:  return warn
                return err

            score_fx = _score_fx(score)
            penalty_fx = _penalty_fx(weather_penalty)

            report = (
                f"{bold(ok(f'Quest completed: {finished.target_icao}! +1 point.'))}\n"
                f"{bold(info('--- ROUTE REPORT ---'))}\n"
                f"{dim(f'Ideal:  {ideal_dist:.0f} km | {ideal_hops} hops | {ideal_fuel:.1f} L')}\n"
                f"{info(f'Yours:  {actual_dist:.0f} km | {actual_hops} hops | {actual_base:.1f} L (route)')}\n"
                f"{penalty_fx(f'Weather impact: +{weather_penalty:.1f} L')}\n"
                f"{bold(score_fx(f'Efficiency: {score}/100 ({grade})'))}"
            )

            self._issue_new_quest()
            if self.state.active_quest:
                report += "\n" + info(f"Next target: {self.state.active_quest.target_icao}.")
            self.state.system_msg = report

        else:
            # no quest-related event this hop
            if not self.state.system_msg.startswith("New quest"):
                self.state.system_msg = ""

        return chosen

    def get_airports(self) -> List[Airport]:
        return self._airports

    def get_target_airport(self) -> Optional[Airport]:
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

    # Messaging for events
    def add_event_message(self, msg: str) -> None:
        self._event_messages.append(msg)
