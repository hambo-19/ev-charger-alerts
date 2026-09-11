#!/usr/bin/env python3
"""
EV Charger Availability Alert
Monitors "Florida Tech / Charger 3" (ChargePoint, 2600 Country Club Rd,
Melbourne, FL) and sends an ntfy.sh push notification when a port opens up.

- Uses only the Python standard library (no pip installs needed).
- Data source: ChargePoint's public map feed (same live data as their app).
- State is kept in state.json (committed back to the repo by the workflow)
  so alerts fire only on transitions, not on every poll.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

STATION_ID = 5544921  # FLORIDA TECH / CHARGER 3, 2600 Country Club Rd
STATION_LABEL = "Florida Tech \u2014 Charger 3"

# Change this to your own secret topic name (must match what you
# subscribe to in the ntfy app). Treat it like a password.
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "fit-charger3-8k2m4q9x")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

# Tight bounding box around the station (keeps responses tiny).
MAP_URL = "https://mc.chargepoint.com/map-prod/v2"
MAP_BODY = {
    "map_data": {
        "screen_width": 1600,
        "screen_height": 1200,
        "map_filter": {"dc_fast": True, "level_2": True, "level_1": True},
        "sw_lon": -80.627,
        "sw_lat": 28.068,
        "ne_lon": -80.623,
        "ne_lat": 28.071,
    }
}

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def http_post_json(url: str, payload: dict, timeout: int = 20) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_station() -> dict:
    data = http_post_json(MAP_URL, MAP_BODY)
    for station in data.get("map_data", {}).get("stations", []):
        if station.get("device_id") == STATION_ID:
            return station
    raise RuntimeError(f"Station {STATION_ID} not found in map response")


def load_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def notify(title: str, message: str, priority: str, tags: str) -> None:
    req = urllib.request.Request(
        NTFY_URL,
        data=message.encode("utf-8"),
        headers={
            "Title": title,
            "Priority": priority,
            "Tags": tags,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        log(f"ntfy sent ({resp.status}): {title}")


def main() -> int:
    try:
        station = fetch_station()
    except Exception as exc:  # network hiccup etc. — don't fail the workflow
        log(f"Fetch failed, skipping this run: {exc}")
        return 0

    ports = station.get("ports", [])
    total = len(ports)
    available = sum(1 for p in ports if p.get("status") == "available")
    log(f"{STATION_LABEL}: {available}/{total} ports available")

    state = load_state()
    prev = state.get("last_available")

    if prev is not None and available > 0 and prev == 0:
        notify(
            f"Charger spot open! \U0001f50c",
            f"{available}/{total} port(s) now available at {STATION_LABEL} "
            f"(2600 Country Club Rd).",
            priority="high",
            tags="electric_plug,car",
        )
    elif prev is not None and available == 0 and prev > 0:
        notify(
            "Charger full again",
            f"All ports are now in use at {STATION_LABEL}.",
            priority="low",
            tags="no_entry",
        )

    state["last_available"] = available
    state["last_total"] = total
    state["last_checked_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
