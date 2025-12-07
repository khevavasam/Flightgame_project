from flask import Flask, jsonify, request, render_template
from game.core.game import Game

app = Flask(__name__)
game = Game()


@app.get("/start")
def start_game():
    game.start()
    return jsonify({"status": "started", "game": game.status()})


@app.get("/status")
def status():
    if not game.is_running():
        return jsonify({"error": "Game not started"}), 400
    return jsonify(game.status())


@app.get("/options")
def options():
    opts = game.options()
    return jsonify(
        [{"icao": a.icao, "name": a.name, "distance_km": dist} for (a, dist) in opts]
    )


@app.post("/pick")
def pick():
    data = request.get_json(silent=True) or {}
    index = data.get("index")
    if not isinstance(index, int):
        return jsonify({"error": "index must be an integer"}), 400

    airport = game.pick(index)
    return jsonify(
        {"picked": airport.icao if airport else None, "status": game.status()}
    )


@app.get("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=8000, debug=True)
