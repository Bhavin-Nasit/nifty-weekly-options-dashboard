# Nifty Weekly Options Writer Dashboard

A modular Streamlit dashboard for tracking weekly Nifty option-writing signals using Zerodha Kite Connect and Discord alerts.

## What it does

- Tracks only NIFTY weekly options.
- Focuses on ATM ± configurable strikes.
- Detects likely Call Writing, Put Writing, Buying, Short Covering, and Long Unwinding.
- Shows PCR, top resistance/support writing zones, and live option-chain table.
- Sends Discord alerts when OI change crosses your threshold.
- Deploys easily on Render.

## Important disclaimer

This is a decision-support dashboard only. It does not place trades. Options selling has high risk, especially near weekly expiry. Always validate signals with price action, risk limits, and margin availability.

## Repo structure

```text
.
├── app.py                  # Streamlit dashboard
├── config.py               # Environment config
├── generate_token.py       # Daily Kite access token helper
├── requirements.txt
├── render.yaml             # Render blueprint
├── src/
│   ├── alerts.py           # Discord alerts
│   ├── data_fetcher.py     # Kite data and Nifty option chain builder
│   ├── kite_client.py      # Kite client factory
│   └── signals.py          # Signal logic
└── .env.example
```

## Environment variables

Set these in Render or in a local `.env` file:

```bash
KITE_API_KEY=your_api_key
KITE_API_SECRET=your_api_secret
KITE_ACCESS_TOKEN=your_daily_access_token
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
STRIKE_RANGE=10
OI_ALERT_THRESHOLD=50000
REFRESH_SECONDS=60
```

## Daily Kite token flow

Kite API key and secret are static. The access token is daily.

```bash
python generate_token.py
```

Open the login URL, copy `request_token` from the redirected URL, paste it into the script, then update `KITE_ACCESS_TOKEN` in Render.

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
