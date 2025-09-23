from .config import get_connection
from game.core import Airport
from typing import Optional, cast, Dict, Any


class AirportRepository:
    @staticmethod
    def get_airport_by_name(name: str) -> Optional[Airport]:
        sql = "SELECT ident, name, iso_country, latitude_deg AS lat, longitude_deg AS lon FROM airport where name LIKE Concat('%', %s,'%')"
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (name,))
            row = cast(Optional[Dict[str, Any]], cur.fetchone())
            if row:
                return Airport(
                    icao=str(row["ident"]),
                    name=str(row["name"]),
                    country=str(row["iso_country"]),
                    lat=float(row["lat"]),
                    lon=float(row["lon"]),
                )
            return None
