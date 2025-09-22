from dataclasses import dataclass


@dataclass
class Airport:
    icao: str
    name: str
    country: str
    lat: float
    lon: float
