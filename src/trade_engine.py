def suggest_trade(calls, puts, spot):
    if not calls.empty and not puts.empty:
        top_call = calls.iloc[0]
        top_put = puts.iloc[0]

        call_strike = int(top_call["strike"])
        put_strike = int(top_put["strike"])

        # Range condition
        if abs(call_strike - put_strike) > 200:
            return "No Trade (Wide spread / unclear range)"

        return f"Range Trade: Sell {put_strike} PE & {call_strike} CE"

    if not puts.empty:
        strike = int(puts.iloc[0]["strike"])
        return f"Bullish: Sell {strike} PE"

    if not calls.empty:
        strike = int(calls.iloc[0]["strike"])
        return f"Bearish: Sell {strike} CE"

    return "No Trade"
