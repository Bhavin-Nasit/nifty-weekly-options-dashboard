import streamlit as st
import time

from src.data_fetcher import get_weekly_nifty_tokens
from src.websocket_live import start_websocket
from src.state_manager import update_snapshot
from src.processor import build_dataframe, get_zones
from src.trade_engine import suggest_trade
from src.alerts import send_discord_alert

st.set_page_config(layout="wide")
st.title("Nifty FII Options Dashboard (LIVE)")

try:
    tokens_df = get_weekly_nifty_tokens()

    token_map = {}
    for _, row in tokens_df.iterrows():
        token_map[int(row["instrument_token"])] = {
            "strike": row["strike"],
            "type": row["instrument_type"]
        }

    tokens = list(token_map.keys())

    st.info(f"Tracking {len(tokens)} instruments...")

    live_ticks = start_websocket(tokens)

    time.sleep(2)

    delta = update_snapshot(live_ticks)

    if delta is None:
        st.warning("Collecting initial snapshot...")
    else:
        df = build_dataframe(delta, token_map)

        calls, puts = get_zones(df)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔴 Resistance (Call Writing)")
            st.dataframe(calls)

        with col2:
            st.subheader("🟢 Support (Put Writing)")
            st.dataframe(puts)

        st.subheader("📊 Trade Suggestion")
        spot_guess = df["strike"].median() if not df.empty else 0
        trade = suggest_trade(calls, puts, spot_guess)
        st.success(trade)

        if not calls.empty:
            strike = int(calls.iloc[0]["strike"])
            send_discord_alert(f"🔴 Call Writing at {strike}", key=f"call_{strike}")

        if not puts.empty:
            strike = int(puts.iloc[0]["strike"])
            send_discord_alert(f"🟢 Put Writing at {strike}", key=f"put_{strike}")

        st.subheader("📈 Signal Table")
        st.dataframe(df)

except Exception as e:
    st.error(str(e))
    st.info("Check Zerodha setup")

st.caption("Live FII signal engine running...")

time.sleep(5)
st.rerun()
