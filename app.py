import time

import streamlit as st

from src.alerts import send_discord_alert
from src.config import REFRESH_SECONDS
from src.market_data import get_market_snapshot
from src.processor import get_zones
from src.trade_engine import suggest_trade


st.set_page_config(layout="wide")
st.title("Nifty FII Options Dashboard")

try:
    snapshot = get_market_snapshot()
    df = snapshot.df

    source_line = f"Source: {snapshot.source}"
    if snapshot.spot:
        source_line += f" | Spot: {snapshot.spot:.2f}"
    st.caption(source_line)

    if snapshot.message:
        st.info(snapshot.message)

    if df.empty:
        st.warning("No option-chain rows available yet. Waiting for the next refresh.")
    else:
        calls, puts = get_zones(df)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Resistance (Call Writing)")
            st.dataframe(calls)

        with col2:
            st.subheader("Support (Put Writing)")
            st.dataframe(puts)

        st.subheader("Trade Suggestion")
        spot_guess = snapshot.spot or df["strike"].median()
        trade = suggest_trade(calls, puts, spot_guess)
        st.success(trade)

        if not calls.empty:
            strike = int(calls.iloc[0]["strike"])
            send_discord_alert(f"Call Writing at {strike}", key=f"call_{strike}")

        if not puts.empty:
            strike = int(puts.iloc[0]["strike"])
            send_discord_alert(f"Put Writing at {strike}", key=f"put_{strike}")

        st.subheader("Signal Table")
        st.dataframe(df)

except Exception as e:
    st.error(str(e))
    st.info("Check the data source settings in Render environment variables.")

st.caption("FII signal engine running...")

time.sleep(REFRESH_SECONDS)
st.rerun()
