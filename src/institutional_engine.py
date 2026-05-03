import pandas as pd

def compute_scores(df: pd.DataFrame):
    df = df.copy()

    df['call_pressure'] = df['ce_oi_change'] - df['ce_ltp_change']
    df['put_pressure'] = df['pe_oi_change'] - df['pe_ltp_change']

    df['institutional_score'] = df['put_pressure'] - df['call_pressure']

    return df


def market_bias(df: pd.DataFrame):
    total_score = df['institutional_score'].sum()

    if total_score > 0:
        return "BULLISH (Put writers dominant)"
    elif total_score < 0:
        return "BEARISH (Call writers dominant)"
    else:
        return "NEUTRAL"


def detect_danger_zones(df, spot, distance):
    danger = []

    for _, row in df.iterrows():
        strike = row['strike']

        if abs(strike - spot) <= distance:
            if "CALL WRITING" in str(row.get('signal', '')):
                danger.append(f"⚠️ Near CALL wall at {strike}")
            if "PUT WRITING" in str(row.get('signal', '')):
                danger.append(f"⚠️ Near PUT wall at {strike}")

    return danger
