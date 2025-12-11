from flask import Flask, jsonify, request, render_template
from game.core.game import Game
from game.db.airport_repo import AirportRepository
from game.core.planning.player_rule_route import compute_player_rule_route

app = Flask(__name__)
game = Game()
repo = AirportRepository()


def _status_with_coords(base_status: dict) -> dict:
    """Return game status dict enriched with current/target coordinates."""
    status = dict(base_status)

    cur_icao = status.get("icao")
    tgt_icao = status.get("quest_target")

    if cur_icao:
        cur = repo.get_by_icao(cur_icao)
        if cur:
            status["current_lat"] = cur.lat
            status["current_lon"] = cur.lon
            status["current_name"] = cur.name

    if tgt_icao:
        tgt = repo.get_by_icao(tgt_icao)
        if tgt:
            status["target_lat"] = tgt.lat
            status["target_lon"] = tgt.lon
            status["target_name"] = tgt.name

    return status


@app.get("/start")
def start_game():
    """Start a new game and return initial status."""
    game.start()
    st = _status_with_coords(game.status())
    return jsonify({"status": "started", "game": st})


@app.get("/status")
def status():
    """Return current game status (with coordinates)."""
    if not game.is_running():
        return jsonify({"error": "Game not started"}), 400
    st = _status_with_coords(game.status())
    return jsonify(st)


@app.get("/options")
def options():
    """Return list of nearest airports with distance and coordinates."""
    opts = game.options()
    return jsonify(
        [
            {
                "icao": a.icao,
                "name": a.name,
                "distance_km": dist,
                "lat": a.lat,
                "lon": a.lon,
            }
            for (a, dist) in opts
        ]
    )


@app.post("/pick")
def pick():
    """Pick next airport by index (1-based) and return updated status."""
    data = request.get_json(silent=True) or {}
    index = data.get("index")

    if not isinstance(index, int):
        return jsonify({"error": "index must be an integer"}), 400

    airport = game.pick(index)
    st = _status_with_coords(game.status())
    return jsonify(
        {
            "picked": airport.icao if airport else None,
            "status": st,
        }
    )


@app.get("/route")
def route():

    if not game.is_running():
        return jsonify({"error": "Game not started"}), 400

    base_status = game.status()
    status = _status_with_coords(base_status)

    cur_icao = status.get("icao")
    tgt_icao = status.get("quest_target")
    country = status.get("country", "FI")

    if not cur_icao or not tgt_icao:
        return jsonify({"error": "Missing current or target airport"}), 400

    start_airport = repo.get_by_icao(cur_icao)
    target_airport = repo.get_by_icao(tgt_icao)

    if not start_airport or not target_airport:
        return jsonify({"error": "Could not resolve airports"}), 400

    all_airports = repo.list_airports(country=country)

    # Use fuel settings from game config when available, otherwise defaults
    fuel_per_km = getattr(getattr(game, "config", None), "fuel_per_km", 0.1)
    fuel_fixed = getattr(getattr(game, "config", None), "fuel_fixed", 10.0)

    result = compute_player_rule_route(
        start_airport=start_airport,
        target_airport=target_airport,
        all_airports=all_airports,
        fuel_per_km=fuel_per_km,
        fuel_fixed=fuel_fixed,
    )

    path = [
        {"icao": a.icao, "name": a.name, "lat": a.lat, "lon": a.lon}
        for a in result.path
    ]

    return jsonify(
        {
            "success": result.success,
            "message": result.message,
            "distance_km": result.distance_km,
            "fuel": result.base_fuel,
            "hops": result.hops,
            "path": path,
        }
    )


@app.get("/")
def index():
    """Render main frontend page."""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=8000, debug=True)
