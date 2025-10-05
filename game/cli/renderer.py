from typing import List
from game.utils.math_helpers import clamp, scale_to_index, normalize
from game.utils.colors import ok, info, err, dim, bold

# Finland min max coordinates for the map scaling
MIN_LAT, MAX_LAT = 59.0, 70.0
MIN_LON, MAX_LON = 20.0, 32.0


# Try to return strings with renderer methods instead of directly printing.
# This makes unit testing in the future easier...
class Renderer:
    def __init__(self) -> None:
        self.map_width = 40
        self.map_height = 30
        self.first_loop = True

    def _to_grid(self, lat: float, lon: float) -> tuple[int, int]:
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

    def draw_game_status(self, status: dict) -> str:
        return (
            f"Current location: {status['name']} ({status['icao']}) - "
            f"hops: {status['hops']}, total km: {status['km_total']} km, "
            f"fuel: {status['fuel']} litres"
        )

    def draw_command_list(self, options_count: int = 5) -> str:
        option_range_str = f"[1-{options_count}]" if options_count > 1 else "[1]  "
        command_lines = [
            bold("🗒 Commands"),
            dim("────────────────────────────────────"),
            f"{ok(option_range_str)}      {dim('Choose next airport to fly to')}",
            f"{info('[m | map]')}  {dim('View map')}",
            f"{info('[quests]')}   {dim('View questlog')}",
            f"{info('[i | r]')}    {dim('Refresh status')}",
            f"{err('[q | exit]')} {dim('Quit')}",
            "",
        ]
        return "\n".join(command_lines)

    def clear_console(self) -> str:
        return "\033[H\033[J"

    def prompt_continue(self) -> str:
        return "Press Enter to Continue..."
