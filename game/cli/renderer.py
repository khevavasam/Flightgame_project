from typing import List
from game.utils.math_helpers import clamp, scale_to_index, normalize

# Finland min max coordinates for the map scaling
MIN_LAT, MAX_LAT = 59.0, 70.0
MIN_LON, MAX_LON = 20.0, 32.0


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

    def clear_console(self):
        print("\033[H\033[J", end="")

    def enter_to_continue(self, input_str: str = "Press Enter to Continue..."):
        if self.first_loop:
            self.first_loop = False
            return ""
        return input(input_str)
