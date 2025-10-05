"""
core/entities/airport.py
========================
Defines the Airport data structure for the game.

Basic information of an airport including ICAO code, name,
country, latitude and longitude coordinates.
"""

from dataclasses import dataclass


@dataclass
class Airport:
    """Represents an aiport with location and basic information."""

    icao: str
    name: str
    country: str
    lat: float
    lon: float
