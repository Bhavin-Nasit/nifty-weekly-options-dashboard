import streamlit as st
import time

from src.config import REFRESH_SECONDS, DANGER_DISTANCE_POINTS
from src.signals import add_institutional_view, pcr
from src.institutional_engine import compute_scores, market_bias, detect_danger_zones

# Placeholder minimal dataset (replace with real fetcher next push)
import pandas as pd

st.title("Nifty Institutional Dashboard (PRO)")

# Dummy data placeholder

data = pd.DataFrame({
    'strike':[23800,23900,24000,24100,24200],
    'ce_oi':[100,200,300,400,500],
    'pe_oi':[500,400,300,200,100],
    'ce_oi_change':[50,100,150,200,250],
    'pe_oi_change':[200,150,100,50,20],
    'ce_ltp_change':[-10,-8,-5,-3,-1],
    'pe_ltp_change':[-2,-4,-6,-8,-10]
})

df = add_institutional_view(data)
df = compute_scores(df)

bias = market_bias(df)

st.metric("Market Bias", bias)

st.subheader("Institutional Signals")
st.dataframe(df)

st.subheader("Danger Zones")
danger = detect_danger_zones(df, 24000, DANGER_DISTANCE_POINTS)
for d in danger:
    st.warning(d)

st.subheader("PCR")
st.write(pcr(df))

st.caption("Auto-refreshing...")
time.sleep(REFRESH_SECONDS)
st.rerun()
