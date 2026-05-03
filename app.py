import streamlit as st
import time

from src.data_fetcher import get_weekly_nifty_tokens
from src.websocket_live import start_websocket

st.title("Nifty Live Institutional Dashboard (Zerodha WebSocket)")

try:
    tokens_df = get_weekly_nifty_tokens()
    tokens = tokens_df['instrument_token'].tolist()

    st.info(f"Subscribing to {len(tokens)} instruments...")

    live_ticks = start_websocket(tokens)

    time.sleep(3)

    if not live_ticks:
        st.warning("Waiting for live ticks...")
    else:
        st.success(f"Live ticks received: {len(live_ticks)}")

        preview = []
        for k, v in list(live_ticks.items())[:15]:
            preview.append({
                "token": k,
                "ltp": v.get("last_price"),
                "oi": v.get("oi"),
                "volume": v.get("volume")
            })

        st.dataframe(preview)

except Exception as e:
    st.error(str(e))
    st.info("Check Kite API key, token, and subscription")

st.caption("Live WebSocket feed active")
