# EV Charger Availability Alert

Get a phone notification the moment a port opens up at
**Florida Tech — Charger 3** (ChargePoint, 2600 Country Club Rd, Melbourne, FL).

## How it works

1. **GitHub Actions** runs `charger_alert.py` every 5 minutes (free on public repos).
2. The script queries ChargePoint's public map feed for live port status.
3. When availability changes, it pushes a notification through **ntfy.sh** to
   everyone subscribed to the topic — no accounts, no cost.

## Setup (one time, ~5 minutes)

1. **Choose a secret topic name** — a random string like `fit-charger3-8k2m4q9x`.
   Anyone who knows it can see/send alerts, so keep it unguessable.
2. Set it in **either** place:
   - Repo → Settings → Secrets and variables → Actions → **Variables** tab →
     new variable `NTFY_TOPIC`, **or**
   - Edit the default value of `NTFY_TOPIC` in `charger_alert.py`.
3. On your phone: install the **ntfy** app (iOS / Android / F-Droid), tap
   **+**, subscribe to your topic name.
4. Done — you'll get a push the next time a spot opens.

To share with others: just give them the topic name and have them subscribe
in the ntfy app.

## Test it

Actions tab → "Charger availability poll" → **Run workflow** → check the run
log for the current port count. (Test alerts only fire on real state
transitions; to test your phone subscription, publish any message to your
topic from <https://ntfy.sh>.)

## Files

| File | Purpose |
|---|---|
| `charger_alert.py` | Polls ChargePoint, sends ntfy alerts (stdlib only) |
| `state.json` | Last known availability — committed back each run |
| `.github/workflows/poll.yml` | 5-minute schedule + state commit + monthly keep-alive |

## Notes

- The map feed is undocumented but public; if ChargePoint changes it, the
  script logs an error instead of sending false alerts.
- GitHub disables scheduled workflows after 60 days of repo inactivity; the
  workflow commits a monthly `keepalive.txt` marker to prevent that.
