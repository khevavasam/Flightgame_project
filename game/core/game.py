from game.db import AirportRepository


class Game:
    def __init__(self) -> None:
        self.running = True

    def get_airport_by_name(self, name: str):
        return AirportRepository.get_airport_by_name(name) if not None else ""

    def exit_game(self):
        self.running = False

    def is_running(self) -> bool:
        return self.running
