from game.core import Game
from geopy.distance import geodesic
from game.core.input import handle_input
from .renderer import Renderer
from game.utils.colors import ok, warn, err, info, dim, bold
from typing import Optional
import sys



def _clear_console(renderer):
    print(renderer.clear_console(), end="")

def main_menu():
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


def _colorize_line(line_text: str, delta_val: Optional[int], is_best: bool) -> str:
    if delta_val is None:
        return dim(line_text)
    if delta_val >= 25:
        return ok(line_text)
    if delta_val >= 5:
        return bold(line_text)
    if delta_val < 0:
        return err(line_text)
    return dim(line_text)


def main():
    renderer = Renderer()
    g = Game()
    g.start()

    # Call main menu before main loop
    main_menu()

    # Main loop
    while g.is_running():
        if g.state is None:
            raise ValueError("Game state is None. Call g.start() first.")

        input(renderer.prompt_continue())
        _clear_console(renderer)
        # Status only for renderer.
        st = g.status()
        print(info(renderer.draw_game_status(st)))

        active_quest = g.state.active_quest
        if active_quest:
            rem = g.remaining_distance_to_target()
            print(
                bold(
                    f"Active Quest: Fly to {active_quest.target_icao} - remaining: {rem} km"
                )
            )

        print(dim(f"Points: {g.state.points}"))
        if g.state.system_msg:
            print(warn(g.state.system_msg))

        opts = g.options()
        best_idx = None
        best_delta = None

        target_airport = g.get_target_airport() if active_quest else None
        cur_to_target_km = g.remaining_distance_to_target() if active_quest else None

        for i, (a, d) in enumerate(opts, start=1):
            line = f"{i}. {a.name} ({a.icao}) — ~{d:.0f} km"

            delta = None
            mark = ""
            if target_airport and cur_to_target_km is not None:
                dist_next = geodesic(
                    (a.lat, a.lon), (target_airport.lat, target_airport.lon)
                ).km
                delta = cur_to_target_km - int(round(dist_next))
                mark = (
                    "++"
                    if delta >= 25
                    else ("+" if delta >= 5 else ("−" if delta < 0 else "·"))
                )
                line += f"  → Δdist: {delta:+d} km  {mark}"

                if best_delta is None or delta > best_delta:
                    best_delta = delta
                    best_idx = i

            is_best = best_idx == i
            print(_colorize_line(line, delta, is_best))

        if best_idx is not None and best_delta is not None and best_delta > 0:
            best_airport = opts[best_idx - 1][0]
            print(
                ok(
                    f"\nRecommended next hop: {best_idx}) {best_airport.icao} — cuts {best_delta} km"
                )
            )

        print(
            dim(
                "\nCommands: enter option number to fly, "
                "'quests' to view quest log, 'i' to refresh, 'q' or 'exit' to quit."
            )
        )

        # Command pattern implementation
        raw = input("> ").strip()
        result = handle_input(g, raw)
        for msg in result.messages:
            print(msg)
