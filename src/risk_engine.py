from src.config import (
    ACCOUNT_CAPITAL,
    RISK_PER_TRADE_PCT,
    MAX_LOTS,
    NIFTY_LOT_SIZE,
    OPTION_SL_MULTIPLIER,
    OPTION_TARGET_MULTIPLIER,
    SPREAD_WIDTH,
)


def calculate_position_size(premium):
    risk_capital = ACCOUNT_CAPITAL * (RISK_PER_TRADE_PCT / 100)

    sl_per_lot = premium * OPTION_SL_MULTIPLIER * NIFTY_LOT_SIZE

    if sl_per_lot <= 0:
        return 0

    lots = int(risk_capital // sl_per_lot)

    return min(max(lots, 1), MAX_LOTS)


def build_trade_plan(trade, premium=50):
    lots = calculate_position_size(premium)

    sl = premium * OPTION_SL_MULTIPLIER
    target = premium * OPTION_TARGET_MULTIPLIER

    return {
        "trade": trade,
        "lots": lots,
        "entry": premium,
        "sl": round(sl, 2),
        "target": round(target, 2),
        "spread_hedge": SPREAD_WIDTH,
    }
