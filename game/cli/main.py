from game.core import Game
from geopy.distance import geodesic
from .renderer import Renderer
from game.utils.colors import ok, warn, err, info, dim, bold
from typing import Optional


def _clear_console(renderer):
    print(renderer.clear_console(), end="")


def main():
    renderer = Renderer()
    g = Game()
    g.start()

    # Main loop
    while g.is_running():
        input(renderer.prompt_continue())
        _clear_console(renderer)
        st = g.status()
        # Status + quest + points + system messages
        print(info(renderer.draw_game_status(st)))
        if st.get("quest_target"):
            qdist = st.get("quest_distance")
            print(
                bold(
                    f"Active Quest: Fly to {st['quest_target']} - remaining: {qdist} km"
                )
            )
        print(dim(f"Points: {st.get('points', 0)}"))
        if st.get("system_msg"):
            print(warn(st["system_msg"]))
        print()

        opts = g.options()
        best_idx = None
        best_delta = None

        target_icao = st.get("quest_target")
        cur_to_target_km = st.get("quest_distance")
        target_airport = g.get_target_airport() if target_icao else None

        def colorize_line(
            line_text: str, delta_val: Optional[int], is_best: bool
        ) -> str:
            if delta_val is None:
                return dim(line_text)
            if delta_val >= 25:
                return ok(line_text)
            if delta_val >= 5:
                return bold(line_text)
            if delta_val < 0:
                return err(line_text)
            return dim(line_text)

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
            print(colorize_line(line, delta, is_best))

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
        cmd = input("> ").strip().lower()

        if cmd in ("q", "exit"):
            g.exit_game()
            print(info("Goodbye - game ended."))
            break

        if cmd == "quests":
            _clear_console(renderer)
            print(bold("\nQuest Log"))
            if g.quest_active:
                rem = g.remaining_distance_to_target()
                print(
                    f"Active:\n- Fly to {g.quest_active.target_icao} — {rem} km remaining"
                )
            else:
                print("Active:\n- None")
            if g.quest_completed:
                print("\nCompleted:")
                for i, q in enumerate(g.quest_completed, start=1):
                    print(f"{i}) {q.target_icao}")
            else:
                print(dim("\nCompleted:\n- None"))
            print(bold(f"\nTotal points: {g.points}\n"))
            continue

        if cmd == "map":
            _clear_console(renderer)

            legend = " ".join(
                [
                    f"{dim('*')} airports",
                    f"{bold(info('@'))} you",
                    f"{bold(err('X'))} target",
                ]
            )
            print(legend)

            raw = renderer.draw_map(g.current, g.get_target_airport(), g.get_airports())

            palette = {
                "*": dim("*"),
                "@": bold(info("@")),
                "X": bold(err("X")),
            }
            colored_map = "".join(palette.get(ch, ch) for ch in raw)

            print(colored_map)
            continue

        if cmd in ("i", ""):
            continue

        if cmd.isdigit():
            idx = int(cmd)
            if 1 <= idx <= len(opts):
                chosen = g.pick(idx)
                print(info(f"\n>>> Flying to {chosen.name} ({chosen.icao}) >>>"))  # type: ignore
                for event_msg in g._event_messages:
                    print(warn(event_msg))
                st_after = g.status()
                if st_after.get("system_msg"):
                    print(warn(st_after["system_msg"]))
                print()
                continue

        print(err("Invalid command, try again.\n"))
