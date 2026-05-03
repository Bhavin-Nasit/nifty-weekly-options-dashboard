import pandas as pd


def build_dataframe(delta, token_map):
    rows = []

    for token, data in delta.items():
        meta = token_map.get(token)
        if not meta:
            continue

        strike = int(meta["strike"])
        opt_type = meta["type"]

        signal = "NEUTRAL"
        if data["oi_change"] > 0 and data["ltp_change"] < 0:
            signal = f"{opt_type} WRITING"
        elif data["oi_change"] < 0 and data["ltp_change"] > 0:
            signal = f"{opt_type} SHORT COVERING"

        rows.append({
            "strike": strike,
            "type": opt_type,
            "oi_change": data["oi_change"],
            "ltp_change": data["ltp_change"],
            "volume_change": data["volume_change"],
            "signal": signal
        })

    return pd.DataFrame(rows)


def get_zones(df):
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    call_writing = df[(df["type"] == "CE") & (df["signal"].str.contains("WRITING"))]
    put_writing = df[(df["type"] == "PE") & (df["signal"].str.contains("WRITING"))]

    top_calls = call_writing.sort_values("oi_change", ascending=False).head(3)
    top_puts = put_writing.sort_values("oi_change", ascending=False).head(3)

    return top_calls, top_puts
