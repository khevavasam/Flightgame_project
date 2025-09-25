from game.core import Game


def main():
    g = Game()
    g.start()

    # Main loop
    while g.is_running():
        st = g.status()
        print(
            f"Current location: {st['name']} ({st['icao']}) - hops: {st['hops']}, total km: {st['km_total']} km, fuel: {st['fuel']} litres"
        )
        print()
        opts = g.options()
        for i, (a, d) in enumerate(opts, start=1):
            print(f"{i}. {a.name} ({a.icao}) - {d:.0f} km")

        print(
            "\nCommands: enter option number to fly, 'i' to refresh, 'q' or 'exit' to quit."
        )
        cmd = input("> ").strip().lower()

        if cmd in ("q", "exit"):
            g.exit_game()
            print("Goodbye - game ended.")
            break

        if cmd == "i" or cmd == "":
            continue

        if cmd.isdigit():
            idx = int(cmd)
            if 1 <= idx <= len(opts):
                chosen = g.pick(idx)
                print(f"\n>>> Flying to {chosen.name} ({chosen.icao}) >>>")  # type: ignore
                # Weather event triggers in every pick so print the msg here.
                print(g._last_weather_msg + "\n")
                continue

        print("Invalid command, try again.\n")
