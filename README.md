# Nifty Weekly Options Writer Dashboard

A modular Streamlit dashboard for tracking NIFTY option-writing signals with Kite Connect when available and slower free-source fallbacks when it is not.

## What it does

- Tracks NIFTY weekly options.
- Focuses on ATM +/- configurable strikes.
- Detects likely Call Writing, Put Writing, Buying, Short Covering, and Long Unwinding.
- Shows top resistance/support writing zones and the option-chain table.
- Sends Discord alerts when writing zones are detected.
- Deploys on Render.

## Important disclaimer

This is a decision-support dashboard only. It does not place trades. Options selling has high risk, especially near weekly expiry. Always validate signals with price action, risk limits, and margin availability.

## Data sources

Set `DATA_SOURCE` to control the feed:

```bash
DATA_SOURCE=auto      # Kite, NSE snapshot, bhavcopy, then yfinance spot
DATA_SOURCE=free      # NSE snapshot, bhavcopy, then yfinance spot
DATA_SOURCE=kite      # Force Kite Connect live data
DATA_SOURCE=nse       # Force NSE option-chain snapshot
DATA_SOURCE=bhavcopy  # Force NSE delayed end-of-day FO bhavcopy
DATA_SOURCE=yfinance  # Spot-only fallback
```

Kite is the cleanest live source because it supports WebSockets. NSE option-chain is snapshot-based and can be slower or blocked by NSE server rules. The bhavcopy fallback is delayed end-of-day data, but it can still provide NIFTY option OI and change-in-OI rows when the live NSE endpoint is blocked. yfinance is only used for NIFTY spot fallback; it does not provide reliable NFO option-chain OI rows.

## Environment variables

Set these in Render or in a local `.env` file:

```bash
KITE_API_KEY=your_api_key
KITE_API_SECRET=your_api_secret
KITE_ACCESS_TOKEN=your_daily_access_token
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
DATA_SOURCE=free
STRIKE_RANGE=10
OI_ALERT_THRESHOLD=50000
REFRESH_SECONDS=60
NSE_MAX_RETRIES=3
NSE_TIMEOUT_SECONDS=10
BHAVCOPY_LOOKBACK_DAYS=10
YFINANCE_SYMBOL=^NSEI
```

For the free-source version, set:

```bash
DATA_SOURCE=free
```

You can leave Kite values blank when using `DATA_SOURCE=free`, `DATA_SOURCE=nse`, or `DATA_SOURCE=auto`.

## Daily Kite token flow

Kite API key and secret are static. The access token is daily. Update `KITE_ACCESS_TOKEN` in Render after generating the day's token from Kite.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Render

Use these settings:

- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

Or use `render.yaml` as a blueprint.

## Signal interpretation

| Price change | OI change | Signal |
|---|---:|---|
| Down | Up | Writing |
| Up | Up | Buying |
| Up | Down | Short covering |
| Down | Down | Long unwinding |

For CE, heavy writing usually suggests resistance. For PE, heavy writing usually suggests support.
