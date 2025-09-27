from abc import ABC, abstractmethod
from enum import Enum
import random


class GameEvent(ABC):
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def trigger(self, game):
        pass


class WeatherType(Enum):
    CLEAR = 0
    STORM = 1
    RAIN = 2
    SNOW = 3


class WeatherEvent(GameEvent):
    # Feel free to edit or add to these!
    _weather_data = {
        WeatherType.CLEAR: {
            "icon": "☀️",
            "messages": [
                "Sky clear, smooth flying ahead!",
                "Sun shining, perfect conditions for the flight.",
            ],
            "fuel_modifier": 0.0,
            "effect": "Normal fuel consumption.",
        },
        WeatherType.STORM: {
            "icon": "⛈️",
            "messages": [
                "Storm ahead, fasten your seatbelt!",
                "Turbulence alert, incoming storm!",
            ],
            "fuel_modifier": 0.10,
            "effect": "+10% fuel consumed.",
        },
        WeatherType.RAIN: {
            "icon": "🌧️",
            "messages": [
                "Rainy skies ahead, runways may be slippery.",
                "Wet conditions expected, maintain caution!",
            ],
            "fuel_modifier": 0.05,
            "effect": "+5% fuel consumed.",
        },
        WeatherType.SNOW: {
            "icon": "❄️",
            "messages": [
                "Snow is falling, watch out for those icy runways!",
                "Snowy conditions, heavy traffic at the airport expected.",
            ],
            "fuel_modifier": 0.075,
            "effect": "+7.5% fuel consumed.",
        },
    }

    def __init__(self, weather_type: WeatherType) -> None:
        self.weather_type = weather_type

    def description(self) -> str:
        data = self._weather_data[self.weather_type]
        weather_update = (
            f"{data['icon']} {self.weather_type.name.capitalize()} -> {data['effect']}"
        )
        return f"\nWEATHER UPDATE: {weather_update} \n[RADIO]: {random.choice(data['messages'])}"

    def trigger(self, game):
        if not game.state:
            raise ValueError("Game state is None. Call g.start() first.")
        # TODO: refactor fuel consumption logic
        base_consumption = 10.0
        total_usage = base_consumption * (
            1 + self._weather_data[self.weather_type]["fuel_modifier"]
        )
        game.state.player.fuel -= total_usage
        # Save weather event msg for cli to print.
        game._event_messages.append(
            f"{self.description()} (Fuel used: {total_usage:.1f} litres)\n"
        )


class UnionStrikeEvent(GameEvent):
    def description(self) -> str:
        return "\n<<[UNION STRIKE]: FLY TO NEAREST AVAILABLE AIRPORT!>>\n"

    def trigger(self, game):
        game._event_messages.append(f"{self.description()}")
        # Here we should handle or trigger game redirect
        # Currently the event is just placeholder for demo. (not in use)


def get_random_events() -> list[GameEvent]:
    events = []
    events.append(WeatherEvent(random.choice(list(WeatherType))))
    # Here we can add more events later..
    # if random.randint(1, 10) > 5:
    #    events.append(UnionStrikeEvent())
    return events
