"""
cli/main.py
===========
Entry point and main loop for the Flight Game (cli).

Handles:
- Main menu
- Game loop
- Option display with distance deltas
- Colorized CLI output
- Command input handling
"""

from game.core.game import Game
from geopy.distance import geodesic
from game.core.input.input_handler import handle_input
from .renderer import Renderer
from game.utils.colors import ok, warn, err, info, dim, bold
from typing import Optional
import sys


def _clear_console(renderer):
    """Clear the console using renderer escape codes."""
    print(renderer.clear_console(), end="")


def _main_menu():
    """Display the main menu and return the chosen action."""
    print()
    print(bold("✈  Flight Game\n"))
    print(dim("—" * 28))
    print(ok("1)") + " " + info("Start Game") + dim("  (new run)"))
    print(err("2)") + " " + warn("Exit") + dim("       (quit)\n"))

    while True:
        s = input(dim("Choose action (1/2 or q): ")).strip().lower()

        if s in {"q", "quit", "exit"}:
            print()
            sys.exit(0)
        if s == "1":
            print()
            return 1
        if s == "2":
            print()
            sys.exit(0)
        print(err("Invalid option. Use 1, 2 or q."))


# TODO: Refactor coloring logic based on option rankings
def _colorize_line(
    line_text: str, delta_val: Optional[int], is_best: bool, target: bool
) -> str:
    """
    Return a colorized line for an option based on delta, target, and best choice.

    Args:
        line_text (str): The option text to colorize.
        delta_val (Optional[int]): Distance improvement compared to current location.
        is_best (bool): Whether this is the best next hop.
        target (bool): Whether this option is the current quest target.
    """
    if target:
        return warn(line_text)
    if is_best:
        return ok(line_text)
    if delta_val is None:
        return dim(line_text)
    if delta_val >= 10:
        return bold(line_text)
    if delta_val < 10:
        return err(line_text)
    return dim(line_text)


def main():
    """Run the flight game main menu and main loop."""
    renderer = Renderer()
    game = Game()
    game.start()

    # Call main menu before main loop
    _main_menu()

    # Main loop
    while game.is_running():
        if game.state is None:
            raise ValueError("Game state is None. Call g.start() first.")

        input(renderer.prompt_continue())
        _clear_console(renderer)
        # Status only for renderer.
        st = game.status()
        print(info(renderer.draw_game_status(st)))

        active_quest = game.state.active_quest
        if active_quest:
            rem = game.remaining_distance_to_target()
            print(
                bold(
                    f"Active Quest: Fly to {active_quest.target_icao} - remaining: {rem} km"
                )
            )

        print(dim(f"Points: {game.state.points}"))
        if game.state.system_msg:
            print(warn(game.state.system_msg))
            game.state.system_msg = ""

        opts = game.options()

        target_airport = game.get_target_airport() if active_quest else None
        cur_to_target_km = game.remaining_distance_to_target() if active_quest else None

        delta_list = []
        best_idx = None
        best_delta = None

        # 1. Calculate best delta for coloring.
        for i, (a, d) in enumerate(opts, start=1):
            delta = None
            if target_airport and cur_to_target_km is not None:
                dist_next = geodesic(
                    (a.lat, a.lon), (target_airport.lat, target_airport.lon)
                ).km
                delta = cur_to_target_km - int(round(dist_next))
                if best_delta is None or delta > best_delta:
                    best_delta = delta
                    best_idx = i
            delta_list.append(delta)

        name_column_width = max(len(a.name + a.icao) for a, _ in opts) + 3
        distance_column_width = max(len(f"{int(round(d))}") for _, d in opts)

        # 2. Print options and colorize.
        for i, ((a, d), delta) in enumerate(zip(opts, delta_list), start=1):
            name_and_icao = f"{a.name} ({a.icao})"
            line = f"{i:2}. {name_and_icao:<{name_column_width}}  —  ~{d:>{distance_column_width}.0f} km"

            mark = ""
            if delta is not None:
                mark = (
                    "++"
                    if delta >= 25
                    else ("+" if delta >= 5 else ("-" if delta < 0 else "."))
                )
            line += f"  → Δdist: {delta:+4d} km  {mark}"
            is_best = best_idx == i

            print(_colorize_line(line, delta, is_best, target_airport == a))

        if best_idx is not None and best_delta is not None and best_delta > 0:
            best_airport = opts[best_idx - 1][0]
            print(
                ok(
                    f"\nRecommended next hop: {best_idx}) {best_airport.icao} — cuts {best_delta} km\n"
                )
            )

        print(renderer.draw_command_list(len(opts)))

        # Command pattern implementation
        raw = input("> ").strip()
        _clear_console(renderer)
        result = handle_input(game, raw)
        for msg in result.messages:
            print(msg)
