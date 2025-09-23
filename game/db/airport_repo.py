from typing import Optional, List, Dict, Any, Sequence, cast
from .config import get_connection
from game.core import Airport


def _row_to_airport(row: Dict[str, Any]) -> Airport:
    return Airport(
        icao=str(row["ident"]),
        name=str(row["name"]),
        country=str(row["iso_country"]),
        lat=float(row["lat"]),
        lon=float(row["lon"]),
    )


class AirportRepository:

    @staticmethod
    def get_by_icao(icao: str) -> Optional[Airport]:

        sql = """
            SELECT ident, name, iso_country, latitude_deg AS lat, longitude_deg AS lon
            FROM airport
            WHERE ident = %s
            LIMIT 1
        """
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (icao.upper(),))
            row = cast(Optional[Dict[str, Any]], cur.fetchone())
        return _row_to_airport(row) if row else None

    @staticmethod
    def list_airports(
        country: str = "FI",
        allow_types: Sequence[str] = ("small_airport", "medium_airport", "large_airport"),
    ) -> List[Airport]:

        placeholders = ",".join(["%s"] * len(allow_types))
        sql = f"""
            SELECT ident, name, iso_country, latitude_deg AS lat, longitude_deg AS lon
            FROM airport
            WHERE iso_country = %s
              AND type IN ({placeholders})
              AND latitude_deg IS NOT NULL AND longitude_deg IS NOT NULL
              AND latitude_deg <> 0 AND longitude_deg <> 0
            ORDER BY name
        """
        params = (country, *allow_types)
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, params)
            rows = cast(List[Dict[str, Any]], cur.fetchall())

        return [_row_to_airport(r) for r in rows]
