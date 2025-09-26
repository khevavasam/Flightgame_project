from game.core import Game
from geopy.distance import geodesic
from .renderer import Renderer


def main():
    renderer = Renderer()
    g = Game()
    g.start()

    # Main loop
    while g.is_running():
        renderer.enter_to_continue()
        renderer.clear_console()
        st = g.status()
        # Status + quest + points + system messages
        print(
            f"Current location: {st['name']} ({st['icao']}) - "
            f"hops: {st['hops']}, total km: {st['km_total']} km, fuel: {st['fuel']} litres"
        )
        if st.get("quest_target"):
            qdist = st.get("quest_distance")
            print(f"Active Quest: Fly to {st['quest_target']} - remaining: {qdist} km")
        print(f"Points: {st.get('points', 0)}")
        if st.get("system_msg"):
            print(st["system_msg"])
        print()

        opts = g.options()
        best_idx = None
        best_delta = None

        target_icao = st.get("quest_target")
        cur_to_target_km = st.get("quest_distance")
        target_airport = g.get_target_airport() if target_icao else None

        for i, (a, d) in enumerate(opts, start=1):
            line = f"{i}. {a.name} ({a.icao}) - {d:.0f} km"
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
            print(line)

        if best_idx is not None and best_delta is not None and best_delta > 0:
            best_airport = opts[best_idx - 1][0]
            print(
                f"\nRecommended next hop: {best_idx}) {best_airport.icao} — cuts {best_delta} km"
            )

        print(
            "\nCommands: enter option number to fly, "
            "'quests' to view quest log, 'i' to refresh, 'q' or 'exit' to quit."
        )
        cmd = input("> ").strip().lower()

        if cmd in ("q", "exit"):
            g.exit_game()
            print("Goodbye - game ended.")
            break

        if cmd == "quests":
            renderer.clear_console()
            print("\nQuest Log")
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
                print("\nCompleted:\n- None")
            print(f"\nTotal points: {g.points}\n")
            continue

        if cmd.lower() == "map":
            renderer.clear_console()
            print(renderer.draw_map(g.current, g.get_target_airport(), g._airports))
            continue

        if cmd == "i" or cmd == "":
            continue

        if cmd.isdigit():
            idx = int(cmd)
            if 1 <= idx <= len(opts):
                chosen = g.pick(idx)
                print(f"\n>>> Flying to {chosen.name} ({chosen.icao}) >>>")  # type: ignore
                for event_msg in g._event_messages:
                    print(event_msg)
                st_after = g.status()
                if st_after.get("system_msg"):
                    print(st_after["system_msg"])
                print()
                continue

        print("Invalid command, try again.\n")
