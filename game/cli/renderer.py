"""
cli/renderer.py
===============
Handles drawing CLI elements for the flight game.

Includes map rendering, game status, command list, and console utilities.
"""

from typing import List
from game.utils.math_helpers import clamp, scale_to_index, normalize
from game.utils.colors import dim, bold, info, warn

# Finland min max coordinates for the map scaling
MIN_LAT, MAX_LAT = 59.0, 70.0
MIN_LON, MAX_LON = 20.0, 32.0


# Try to return strings with renderer methods instead of directly printing.
# This makes unit testing in the future easier...
class Renderer:
    """Represents a renderer layer for the command line interface."""

    def __init__(self) -> None:
        """Initialize renderer with default map width and height."""
        self.map_width = 40
        self.map_height = 30
        self.first_loop = True

    def _to_grid(self, lat: float, lon: float) -> tuple[int, int]:
        """Convert latitude/longitude to grid coordinates."""
        # Horizontal.
        x_ratio = normalize(lon, MIN_LON, MAX_LON)
        x = scale_to_index(x_ratio, self.map_width)  # Map to column number.
        x = clamp(x, 0, self.map_width - 1)
        # Vertical.
        y_ratio = normalize(lat, MIN_LAT, MAX_LAT)
        y_ratio = 1 - y_ratio  # Flip y to make north top row.
        y = scale_to_index(y_ratio, self.map_height)  # Map to row number.
        y = clamp(y, 0, self.map_height - 1)

        return x, y

    def draw_map(self, current, target, airports: List) -> str:
        """Return a string representing the map with current, target, and airports."""
        map_grid = [[" "] * self.map_width for _ in range(self.map_height)]

        # Place airports in grid.
        for airport in airports:
            x, y = self._to_grid(airport.lat, airport.lon)
            map_grid[y][x] = "*"

        # Mark player's current airport.
        x, y = self._to_grid(current.lat, current.lon)
        map_grid[y][x] = "@"

        # Mark current quest target airport.
        x, y = self._to_grid(target.lat, target.lon)
        map_grid[y][x] = "X"

        # TODO: Mark 5 nearest airports with &

        return "\n".join("".join(row) for row in map_grid)

    def _fuel_progress_bar(self, current: int, max: int = 100) -> str:
        bar_symbols = ("⬜", "🟩", "🟨", "🟥")
        progess_bar = [bar_symbols[0]] * 10
        fuel_ratio = current / max
        symbols_to_fill = int(fuel_ratio * 10)
        if fuel_ratio > 0.7:
            symbol = bar_symbols[1]
        elif fuel_ratio > 0.3:
            symbol = bar_symbols[2]
        else:
            symbol = bar_symbols[3]

        for i in range(symbols_to_fill):
            progess_bar[i] = symbol

        return "".join(progess_bar)

    def _divider(self, width: int = 60) -> str:
        return dim(width * "-")

    def draw_game_status(self, status: dict) -> str:
        """Return a string of the current player's location, hops, distance, and fuel."""
        status_list = [
            f"🗺️ {info('Location:')} {status['name']} ({status['icao']})",
            f"✈️ {info('Hops:')} {status['hops']} | 🌍 {info('Total distance:')} {status['km_total']} km | 🎖️{info('Points:')} {status['points']}",
            f"⛽ {info('Fuel:')} {self._fuel_progress_bar(int(status['fuel']))} {status['fuel']:.1f}/100.0 L",
            f"🎯 {warn('Active quest:')} Fly to {status['quest_target']} 🏁 - remaining {status['quest_distance']} km",
            self._divider(),
        ]
        return "\n".join(status_list)

    def draw_command_list(self, options_count: int = 5) -> str:
        """Return a string with the list of available commands."""
        option_range_str = f"[1-{options_count}]" if options_count > 1 else "[1]  "
        command_lines = [
            bold("🕹️ Commands"),
            self._divider(),
            f"{option_range_str:<12}{dim('Choose next airport to fly to')}",
            f"{'[m | map]':<12}{dim('View map')}",
            f"{'[quests]':<12}{dim('View questlog')}",
            f"{'[i | r]':<12}{dim('Refresh status')}",
            f"{'[q | exit]':<12}{dim('Quit')}",
            "",
        ]
        return "\n".join(command_lines)

    def clear_console(self) -> str:
        """Return escape codes to clear the console."""
        return "\033[H\033[J"

    def prompt_continue(self) -> str:
        """Return the prompt string for pausing the CLI."""
        return "Press Enter to Continue..."
