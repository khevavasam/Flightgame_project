let map;
let markerLayer;
let optionsLayer;
let routeLayer;
let pathLayer;

let currentStatus = null;
let visitedAirports = [];

function initMap() {
  if (map) return;

  map = L.map("map").setView([62, 26], 5);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  markerLayer = L.layerGroup().addTo(map);
  optionsLayer = L.layerGroup().addTo(map);
  routeLayer = L.layerGroup().addTo(map);
  pathLayer = L.layerGroup().addTo(map);
}

function clearLayer(layer) {
  if (layer) layer.clearLayers();
}

async function api(path, body = null) {
  const res = await fetch(path, {
    method: body ? "POST" : "GET",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  return await res.json();
}

function logJson(label, data) {
  const screen = document.getElementById("screen");
  if (!screen) return;
  const prefix = label ? `// ${label}\n` : "";
  screen.innerText = prefix + JSON.stringify(data, null, 2);
}

function stripAnsi(str) {
  if (!str) return "";
  return str.replace(/\x1B\[[0-9;]*m/g, "");
}

function formatSystemMsg(raw) {
  const clean = stripAnsi(raw || "").trim();
  if (!clean) return "";

  const lines = clean
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter((l) => l.length > 0);

  return lines.join("\n");
}

function fuelBarHtml(fuel) {
  const maxFuel = 100;
  const ratio = Math.max(0, Math.min(1, fuel / maxFuel));
  const segments = 10;
  const filled = Math.round(ratio * segments);

  let html = '<div class="fuel-bar">';
  for (let i = 0; i < segments; i++) {
    const cls =
      i < filled ? (ratio > 0.5 ? "fuel-segment ok" : "fuel-segment low") : "fuel-segment empty";
    html += `<span class="${cls}"></span>`;
  }
  html += ` <span class="fuel-label">${fuel.toFixed(1)} / 100 L</span>`;
  html += "</div>";
  return html;
}

function updateStatusUI(status) {
  const el = document.getElementById("statusPanel");
  if (!status || status.error) {
    el.innerHTML = `
      <div class="panel-header"><h2>Player status</h2></div>
      <p>No active game. Press <strong>Start Game</strong> to begin.</p>
    `;
    return;
  }

  el.innerHTML = `
    <div class="panel-header">
      <h2>Player status</h2>
    </div>
    <div class="status-grid">
      <div>
        <p><span class="label">Location</span><br>${status.name} (${status.icao})</p>
      </div>
      <div>
        <p><span class="label">Hops</span><br>${status.hops}</p>
      </div>
      <div>
        <p><span class="label">Distance</span><br>${status.km_total} km</p>
      </div>
      <div>
        <p><span class="label">Points</span><br>${status.points}</p>
      </div>
    </div>
    ${fuelBarHtml(status.fuel)}
  `;
}

function updateQuestUI(status) {
  const el = document.getElementById("questPanel");
  if (!status || status.error) {
    el.innerHTML = "";
    return;
  }

  const targetLabel = status.target_name
    ? `${status.quest_target} (${status.target_name})`
    : status.quest_target;

  const sysMsg = formatSystemMsg(status.system_msg);
  const hasReport = Boolean(sysMsg);

  el.innerHTML = `
    <div class="panel-header">
      <h2>Active quest</h2>
    </div>
    <p class="quest-title">Fly to <strong>${targetLabel}</strong>.</p>
    <p class="quest-remaining">
      Remaining distance: <strong>${status.quest_distance} km</strong>
    </p>
    ${
      hasReport
        ? `<div class="quest-log">${sysMsg.replace(/\n/g, "<br>")}</div>`
        : ""
    }
  `;
}

function recordVisitedFromStatus(status) {
  const lat = status.current_lat;
  const lon = status.current_lon;
  if (typeof lat !== "number" || typeof lon !== "number") return;

  const last = visitedAirports[visitedAirports.length - 1];
  if (!last || last.icao !== status.icao) {
    visitedAirports.push({
      icao: status.icao,
      name: status.name,
      lat,
      lon,
    });
  }
}

function updateHistoryUI() {
  const el = document.getElementById("historyList");
  if (!visitedAirports.length) {
    el.innerHTML = "<p>No flights yet.</p>";
    return;
  }

  el.innerHTML = visitedAirports
    .map(
      (a, idx) => `
      <div class="history-item">
        <span class="step">#${idx + 1}</span>
        <div class="history-text">
          <div>${a.name}</div>
          <div class="icao">${a.icao}</div>
        </div>
      </div>
    `,
    )
    .join("");
}

function updateMarkersFromStatus(status) {
  if (!map) return;
  clearLayer(markerLayer);
  clearLayer(pathLayer);

  recordVisitedFromStatus(status);

  const lat = status.current_lat;
  const lon = status.current_lon;
  const tLat = status.target_lat;
  const tLon = status.target_lon;

  const boundsPoints = [];

  if (typeof lat === "number" && typeof lon === "number") {
    const cur = L.circleMarker([lat, lon], {
      radius: 8,
      color: "#2563eb",
      fillColor: "#2563eb",
      fillOpacity: 0.9,
    })
      .addTo(markerLayer)
      .bindPopup(`You are here:<br>${status.name} (${status.icao})`);
    boundsPoints.push(cur.getLatLng());
  }

  if (typeof tLat === "number" && typeof tLon === "number") {
    const tgt = L.circleMarker([tLat, tLon], {
      radius: 8,
      color: "#f97316",
      fillColor: "#f97316",
      fillOpacity: 0.9,
    })
      .addTo(markerLayer)
      .bindPopup(
        `Quest target:<br>${status.quest_target}${
          status.target_name ? ` (${status.target_name})` : ""
        }`,
      );
    boundsPoints.push(tgt.getLatLng());
  }

  if (visitedAirports.length > 1) {
    const coords = visitedAirports.map((a) => [a.lat, a.lon]);
    L.polyline(coords, {
      color: "#38bdf8",
      weight: 4,
      opacity: 0.85,
    }).addTo(pathLayer);
  }

  if (boundsPoints.length) {
    const bounds = L.latLngBounds(boundsPoints);
    map.fitBounds(bounds, { padding: [40, 40] });
  }
}

function drawOptionsOnMap(status, options) {
  if (!map) return;
  clearLayer(optionsLayer);

  if (!options || !options.length) return;

  const lat = status.current_lat;
  const lon = status.current_lon;
  const from =
    typeof lat === "number" && typeof lon === "number" ? [lat, lon] : null;

  options.forEach((opt) => {
    if (typeof opt.lat === "number" && typeof opt.lon === "number") {
      const pos = [opt.lat, opt.lon];

      L.marker(pos)
        .addTo(optionsLayer)
        .bindPopup(
          `<strong>${opt.name}</strong><br>${opt.icao}<br>${opt.distance_km.toFixed(
            1,
          )} km away`,
        );

      if (from) {
        L.polyline([from, pos], {
          color: "#ef4444",
          weight: 2,
          opacity: 0.7,
          dashArray: "4 4",
        }).addTo(optionsLayer);
      }
    }
  });
}

function drawRouteOnMap(status, routeData) {
  if (!map) return;
  clearLayer(routeLayer);

  if (!routeData || !routeData.success || !routeData.path?.length) return;

  const pathCoords = routeData.path.map((p) => [p.lat, p.lon]);
  L.polyline(pathCoords, {
    color: "#22c55e",
    weight: 4,
    opacity: 0.9,
  }).addTo(routeLayer);

  const lat = status.current_lat;
  const lon = status.current_lon;
  const tLat = status.target_lat;
  const tLon = status.target_lon;
  if (
    typeof lat === "number" &&
    typeof lon === "number" &&
    typeof tLat === "number" &&
    typeof tLon === "number"
  ) {
    L.polyline(
      [
        [lat, lon],
        [tLat, tLon],
      ],
      {
        color: "#9ca3af",
        weight: 2,
        opacity: 0.8,
        dashArray: "6 4",
      },
    ).addTo(routeLayer);
  }
}

async function fetchOptions() {
  initMap();
  const opts = await api("/options");
  logJson("OPTIONS", opts);

  const list = document.getElementById("optionList");
  if (!opts || !opts.length) {
    list.innerHTML = "<p>No options available. Start the game first.</p>";
  } else {
    list.innerHTML = opts
      .map(
        (opt, idx) => `
        <button class="option-card" onclick="pickOption(${idx + 1})">
          <div class="option-header">
            <span class="badge">#${idx + 1}</span>
            <span class="icao">${opt.icao}</span>
          </div>
          <div class="option-name">${opt.name}</div>
          <div class="option-meta">${opt.distance_km.toFixed(
            1,
          )} km away</div>
        </button>
      `,
      )
      .join("");
  }

  if (currentStatus && !currentStatus.error) {
    drawOptionsOnMap(currentStatus, opts);
  }
}

function hideStartOverlay() {
  const el = document.getElementById("startOverlay");
  if (el) el.classList.add("hidden");
}

function showStartOverlay() {
  const el = document.getElementById("startOverlay");
  if (el) el.classList.remove("hidden");
}

function applyStatus(status) {
  currentStatus = status;
  updateStatusUI(status);
  updateQuestUI(status);
  updateHistoryUI();
  updateMarkersFromStatus(status);
}

async function startGame() {
  initMap();
  hideStartOverlay();

  const data = await api("/start");
  logJson("START", data);
  if (!data.game) return;

  visitedAirports = [];
  applyStatus(data.game);
  await fetchOptions();
  await fetchRoute();
}

async function fetchStatus() {
  initMap();
  const data = await api("/status");
  logJson("STATUS", data);
  if (!data.error) {
    applyStatus(data);
  }
}

async function pickOption(index) {
  initMap();
  const data = await api("/pick", { index });
  logJson("PICK", data);
  if (!data.status || data.status.error) return;

  applyStatus(data.status);
  await fetchOptions();
  await fetchRoute();
}

async function fetchRoute() {
  if (!currentStatus || currentStatus.error) return;
  initMap();
  const data = await api("/route");
  logJson("ROUTE", data);
  if (!data.error) {
    drawRouteOnMap(currentStatus, data);
  }
}

function showRoute() {
  fetchRoute();
}

window.startGame = startGame;
window.fetchStatus = fetchStatus;
window.fetchOptions = fetchOptions;
window.pickOption = pickOption;
window.showRoute = showRoute;

document.addEventListener("DOMContentLoaded", () => {
  initMap();
  showStartOverlay();
});
