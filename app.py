import time

import streamlit as st

from src.alerts import send_discord_alert
from src.config import REFRESH_SECONDS
from src.market_data import get_market_snapshot
from src.processor import get_zones
from src.trade_engine import suggest_trade


def _fmt_number(value):
    try:
        return f"{float(value):,.0f}"
    except (TypeError, ValueError):
        return "0"


def _fmt_points(value):
    try:
        return f"{float(value):+,.2f}"
    except (TypeError, ValueError):
        return "+0.00"


def _zone_explanation(zone_df, option_type):
    if zone_df.empty:
        if option_type == "CE":
            return "No clear call-writing resistance is visible in the current table."
        return "No clear put-writing support is visible in the current table."

    row = zone_df.iloc[0]
    strike = int(row["strike"])
    oi_change = _fmt_number(row.get("oi_change", 0))
    ltp_change = _fmt_points(row.get("ltp_change", 0))
    volume_change = _fmt_number(row.get("volume_change", 0))

    if option_type == "CE":
        return (
            f"Top resistance is near {strike}. Call OI increased by {oi_change} "
            f"while call premium changed {ltp_change}, with volume change around "
            f"{volume_change}. That usually means fresh call sellers are active "
            f"there; they prefer NIFTY to stay below this strike, so the level can "
            f"act as resistance."
        )

    return (
        f"Top support is near {strike}. Put OI increased by {oi_change} "
        f"while put premium changed {ltp_change}, with volume change around "
        f"{volume_change}. That usually means fresh put sellers are active "
        f"there; they prefer NIFTY to stay above this strike, so the level can "
        f"act as support."
    )


def _signal_guide():
    return """
- **CE WRITING**: Call OI is rising while call premium is falling. Fresh call sellers may be building resistance near that strike.
- **PE WRITING**: Put OI is rising while put premium is falling. Fresh put sellers may be building support near that strike.
- **CE LONG UNWINDING**: Call OI is falling while call premium is falling. Call buyers may be exiting, so upside enthusiasm is cooling.
- **PE LONG UNWINDING**: Put OI is falling while put premium is falling. Put buyers may be exiting, so downside fear is cooling.
- **CE SHORT COVERING**: Call OI is falling while call premium is rising. Call sellers may be exiting, which can support an upward move.
- **PE SHORT COVERING**: Put OI is falling while put premium is rising. Put sellers may be exiting, which can weaken support.
- **CE BUYING / PE BUYING**: OI and premium are both rising. Buyers are adding positions in that option type.
"""


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
        st.warning("No option-chain rows are available from the active fallback source.")
    else:
        calls, puts = get_zones(df)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Resistance (Call Writing)")
            st.dataframe(calls)
            st.caption(_zone_explanation(calls, "CE"))

        with col2:
            st.subheader("Support (Put Writing)")
            st.dataframe(puts)
            st.caption(_zone_explanation(puts, "PE"))

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
        with st.expander("Signal meanings", expanded=True):
            st.markdown(_signal_guide())

except Exception as e:
    st.error(str(e))
    st.info("Check the data source settings in Render environment variables.")

st.caption("FII signal engine running...")

time.sleep(REFRESH_SECONDS)
st.rerun()
