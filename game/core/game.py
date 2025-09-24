from __future__ import annotations
from typing import List, Tuple, Optional
from geopy.distance import geodesic
from game.db import AirportRepository
from game.core import Airport
from .events.game_event import WeatherEvent, WeatherType
import random


class Game:
    START_ICAO = "EFHK"
    COUNTRY = "FI"
    START_FUEL: float = 100.0

    def __init__(self) -> None:
        self.running: bool = True
        self.current: Optional[Airport] = None
        self.km_total: float = 0.0
        self.hops: int = 0
        self.resources = {"fuel": self.START_FUEL}
        self._airports: List[Airport] = []
        self._last_options: List[Tuple[Airport, float]] = []
        self._last_weather_msg = ""

    def start(self) -> None:
        self.current = AirportRepository.get_by_icao(self.START_ICAO)
        if not self.current:
            raise RuntimeError("Start airport EFHK not found in DB")
        self._airports = AirportRepository.list_airports(country=self.COUNTRY)
        self.km_total = 0.0
        self.hops = 0
        self._last_options = []

    def status(self) -> dict:
        cur = self.current
        return {
            "icao": cur.icao if cur else None,
            "name": cur.name if cur else None,
            "country": cur.country if cur else None,
            "km_total": int(round(self.km_total)),
            "hops": self.hops,
            "fuel": self.resources["fuel"],
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

        # Temp fuel consumption
        base_consumption = (
            10.0  # 10 units/litres for now. This should be calculated from distance.
        )
        event = WeatherEvent(random.choice(list(WeatherType)))
        radio_msg = event.trigger()
        modifier = event.fuel_modifier()
        total_usage = base_consumption * (1 + modifier)
        self.resources["fuel"] -= total_usage
        # Save weather event msg for cli to print.
        self._last_weather_msg = f"{radio_msg} (Fuel used: {total_usage:.1f} L)"

        return chosen

    def exit_game(self) -> None:
        self.running = False

    def is_running(self) -> bool:
        return self.running
