import pandas as pd

def institutional_signal(row):
    # Core FII-style logic
    if row['ce_oi_change'] > 0 and row['ce_ltp_change'] < 0:
        return "CALL WRITING (Resistance build)"
    if row['pe_oi_change'] > 0 and row['pe_ltp_change'] < 0:
        return "PUT WRITING (Support build)"
    if row['ce_oi_change'] < 0 and row['ce_ltp_change'] > 0:
        return "CALL SHORT COVERING"
    if row['pe_oi_change'] < 0 and row['pe_ltp_change'] > 0:
        return "PUT SHORT COVERING"
    return "NEUTRAL"

def add_institutional_view(df):
    df = df.copy()
    df['signal'] = df.apply(institutional_signal, axis=1)
    return df

def pcr(df):
    call = df['ce_oi'].sum()
    put = df['pe_oi'].sum()
    return round(put / call, 2) if call else 0
