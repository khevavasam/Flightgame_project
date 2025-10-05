"""
core/events/game_event.py
=========================
Defines a GameEvent interface and concrete events for weather conditions and union strikes.

Includes a helper to generate random events.
"""

from abc import ABC, abstractmethod
from enum import Enum
import random


class GameEvent(ABC):
    """Abstract base class for game events."""

    @abstractmethod
    def description(self) -> str:
        """A short description of the event."""
        ...

    @abstractmethod
    def trigger(self, game):
        """Trigger the event's effect in the game."""
        ...


class WeatherType(Enum):
    """Types for different weather conditions."""

    CLEAR = 0
    STORM = 1
    RAIN = 2
    SNOW = 3
    TAILWIND = 4


class WeatherEvent(GameEvent):
    """Weather related game event affecting fuel consumption."""

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
        WeatherType.TAILWIND: {
            "icon": "💨",
            "messages": [
                "Winds at your back, smooth and quick flight ahead.",
                "Enjoy the speed boost from the tailwind!",
            ],
            "fuel_modifier": -0.05,
            "effect": "-5% fuel consumed due to tailwind.",
        },
    }

    def __init__(self, weather_type: WeatherType) -> None:
        """Initialize with a specific WeatherType."""
        self.weather_type = weather_type

    def description(self) -> str:
        """Return a radio message and update message for a specific weather type."""
        data = self._weather_data[self.weather_type]
        weather_update = (
            f"{data['icon']} {self.weather_type.name.capitalize()} -> {data['effect']}"
        )
        return f"\nWEATHER UPDATE: {weather_update} \n[RADIO]: {random.choice(data['messages'])}"

    def trigger(self, game):
        """Apply fuel consumption and save the event message in the game."""
        if not game.state:
            raise ValueError("Game state is None. Call g.start() first.")

        mod = 1.0 + self._weather_data[self.weather_type]["fuel_modifier"]
        if not hasattr(game, "_fuel_factor"):
            game._fuel_factor = 1.0
        game._fuel_factor *= mod

        game._event_messages.append(
            f"{self.description()} (Fuel factor ×{mod:.2f})\n"
        )


class UnionStrikeEvent(GameEvent):
    """Represents a union strike event. [WIP]"""

    def description(self) -> str:
        return "\n<<[UNION STRIKE]: FLY TO NEAREST AVAILABLE AIRPORT!>>\n"

    def trigger(self, game):
        game._event_messages.append(f"{self.description()}")
        # Here we should handle or trigger game redirect
        # Currently the event is just placeholder for demo. (not in use)


def get_random_events() -> list[GameEvent]:
    """Generate a list of random game events."""
    events = []
    events.append(WeatherEvent(random.choice(list(WeatherType))))
    # Here we can add more events later..
    # if random.randint(1, 10) > 5:
    #    events.append(UnionStrikeEvent())
    return events
