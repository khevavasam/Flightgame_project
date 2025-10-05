"""Compute player flight routes based on distance and fuel rules.

This module provides a simple pathfinding algorithm used to estimate
a player's possible flight route between airports.

Includes:
    - `RouteResult`: dataclass describing route metrics.
    - `_km`: distance helper using `geopy`.
    - `compute_player_rule_route`: main function implementing the rule-based routing.
"""

from dataclasses import dataclass
from typing import Iterable, List
from geopy.distance import geodesic
from game.core.entities.airport import Airport


@dataclass
class RouteResult:
    """Represents the result of a computed flight route."""

    path: List[Airport]
    hops: int
    distance_km: float
    base_fuel: float
    success: bool
    message: str = ""


def _km(a: Airport, b: Airport) -> float:
    """Return the great-circle distance between two airports in kilometers."""
    return geodesic((a.lat, a.lon), (b.lat, b.lon)).km


def compute_player_rule_route(
    start_airport: Airport,
    target_airport: Airport,
    all_airports: Iterable[Airport],
    fuel_per_km: float,
    fuel_fixed: float,
    k_neighbors: int = 5,
) -> RouteResult:
    """
    Compute a simple greedy route between two airports.

    Args:
        start_airport: Starting airport.
        target_airport: Destination airport.
        all_airports: Iterable of available airports.
        fuel_per_km: Fuel cost per kilometer.
        fuel_fixed: Fixed cost per leg.
        k_neighbors: Number of nearest candidates to consider.

    Returns:
        RouteResult: Result with path, distance, hops, fuel usage, and success flag.
    """
    airports = list(all_airports)
    if not airports:
        return RouteResult([], 0, 0.0, 0.0, False, "no airports")

    # try to find start/target by object identity, otherwise by ICAO code
    def idx_of(x: Airport) -> int:
        try:
            return airports.index(x)
        except ValueError:
            for i, a in enumerate(airports):
                if a.icao == x.icao:
                    return i
            return -1

    s = idx_of(start_airport)
    t = idx_of(target_airport)
    if s < 0 or t < 0:
        return RouteResult([], 0, 0.0, 0.0, False, "start/target not in list")
    if s == t:
        a = airports[s]
        return RouteResult([a], 0, 0.0, 0.0, True, "start==target")

    cur = airports[s]
    target = airports[t]
    path = [cur]
    total_km = 0.0
    total_fuel = 0.0

    # simple loop: at each step take K nearest candidates that move closer to the target,
    # and pick the one with the maximum distance reduction (tie-breaker: lower hop cost).
    while cur.icao != target.icao:
        cur_to_target = _km(cur, target)

        # candidates that actually reduce the distance to the target
        cand = []
        for a in airports:
            if a.icao == cur.icao:
                continue
            nxt_to_target = _km(a, target)
            if nxt_to_target >= cur_to_target:
                continue
            leg_km = _km(cur, a)
            cand.append((leg_km, a, nxt_to_target))

        if not cand:
            return RouteResult(
                path,
                max(0, len(path) - 1),
                total_km,
                total_fuel,
                False,
                "no forward options",
            )

        # take the k nearest by current leg distance
        cand.sort(key=lambda x: x[0])
        cand = cand[: max(1, k_neighbors)]

        # selection: maximize distance reduction (delta); if equal, minimize hop cost
        best_leg, best_airport = None, None
        best_delta, best_cost = -1.0, float("inf")
        for leg_km, a, nxt_to_target in cand:
            delta = cur_to_target - nxt_to_target
            hop_cost = fuel_fixed + fuel_per_km * leg_km
            if (delta > best_delta) or (delta == best_delta and hop_cost < best_cost):
                best_delta, best_cost = delta, hop_cost
                best_leg, best_airport = leg_km, a

        total_km += best_leg  # type: ignore
        total_fuel += fuel_fixed + fuel_per_km * best_leg  # type: ignore
        cur = best_airport  # type: ignore
        path.append(cur)

    hops = max(0, len(path) - 1)
    return RouteResult(path, hops, total_km, total_fuel, True, "ok")
