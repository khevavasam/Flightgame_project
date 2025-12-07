(async () => {
  "use strict";

  const api = (path, body) =>
    fetch(
      path.startsWith("/") ? path : "/" + path,
      body
        ? {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }
        : undefined,
    ).then((response) => response.json());

  function render(data) {
    document.getElementById("screen").innerText = JSON.stringify(data, null, 2);
  }

  async function start_game() {
    render(await api("/start"));
  }

  async function get_game_status() {
    render(await api("/status"));
  }

  async function get_game_options() {
    const opts = await api("/options");
    render(opts);

    const container = document.getElementById("optionButtons");
    container.innerHTML = "";

    opts.forEach((opt, i) => {
      const btn = document.createElement("button");
      btn.innerText = `Pick ${i + 1}: ${opt.name} (${opt.icao})`;
      btn.onclick = () => pick_game_option(i + 1);
      container.appendChild(btn);
    });
  }

  async function pick_game_option(idx) {
    const result = await api("/pick", { index: idx });
    if (!result.picked) {
      alert(
        "Invalid pick!",
      );
    }
    render(result);
    get_game_options();
  }

  window.start_game = start_game;
  window.get_game_status = get_game_status;
  window.get_game_options = get_game_options;
  window.pick_game_option = pick_game_option;
})();
