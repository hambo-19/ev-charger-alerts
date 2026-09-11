# EV Charger Availability Alert

Get a phone notification the moment a port opens up at
**Florida Tech — Charger 3** (ChargePoint, 2600 Country Club Rd, Melbourne, FL).

## How it works

1. **GitHub Actions** runs `charger_alert.py` every 5 minutes (free on public repos).
2. The script queries ChargePoint's public map feed for live port status.
3. When availability changes, it pushes a notification through **ntfy.sh** to
   everyone subscribed to the topic — no accounts, no cost.

## Get the alerts on your phone

1. Install the **ntfy** app (iOS / Android / F-Droid) — free, no account.
2. Tap **+** and subscribe to topic: **`fit-charger3-alerts-x7k2`**
3. To share with others: just give them that topic name. Anyone who knows it
   can receive (and publish to) the topic, so share it with people, not publicly.

## Test it

Actions tab → "Charger availability poll" → **Run workflow** → check the run
log for the current port count. Alerts fire only on real state transitions.

## Files

| File | Purpose |
|---|---|
| `charger_alert.py` | Polls ChargePoint, sends ntfy alerts (stdlib only) |
| `state.json` | Seed state — live state is kept in the Actions cache |
| `.github/workflows/poll.yml` | 5-minute schedule + state cache + monthly keep-alive |

## Notes

- The map feed is undocumented but public; if ChargePoint changes it, the
  script logs an error instead of sending false alerts.
- GitHub disables scheduled workflows after 60 days of repo inactivity; the
  workflow commits a monthly `keepalive.txt` marker to prevent that.
