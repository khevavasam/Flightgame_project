from abc import ABC, abstractmethod
from enum import Enum
import random

# TODO: Different kind of events.
# Ideas: Event for strikes(lakko)?
# - Player cant land on the chosen airport cause of a airport worker strike and flies to nearest airport...


class GameEvent(ABC):
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def trigger(self) -> str:
        print(self.description())


class WeatherType(Enum):
    CLEAR = 0
    STORM = 1
    RAIN = 2
    SNOW = 3


class WeatherEvent(GameEvent):
    # Flight control(radio) messages.
    # Feel free to edit or add to these!
    _messages = {
        WeatherType.CLEAR: [
            "The sky is clear, smooth flying ahead!",
            "The sun is shining, perfect conditions for the flight.",
        ],
        WeatherType.STORM: [
            "Storm ahead, buckle up!",
            "Turbulence alert, incoming storm!",
        ],
        WeatherType.RAIN: [
            "Rainy skies ahead, runways may be slippery.",
            "Wet conditions expected, maintain caution!",
        ],
        WeatherType.SNOW: [
            "Snow is falling, watch out for those icy runways!",
            "Snowy conditions, heavy traffic at the airport expected.",
        ],
    }

    # fuel consumption modifiers
    _modifiers = {
        WeatherType.CLEAR: 0.0,
        WeatherType.STORM: 0.10,
        WeatherType.RAIN: 0.05,
        WeatherType.SNOW: 0.075,
    }

    def __init__(self, weather_type: WeatherType) -> None:
        self.weather_type = weather_type

    def description(self) -> str:
        random_msg = random.choice(self._messages[self.weather_type])
        return f"[RADIO]: {random_msg}"

    def trigger(self) -> str:
        return self.description()

    def fuel_modifier(self) -> float:
        return self._modifiers[self.weather_type]
