from __future__ import annotations

import time
from dataclasses import dataclass

import pandas as pd

from src.bhavcopy_client import fetch_bhavcopy_snapshot
from src.config import DATA_SOURCE, KITE_API_KEY, UNDERLYING, YFINANCE_SYMBOL
from src.data_fetcher import get_weekly_nifty_tokens
from src.nse_client import fetch_nse_option_snapshot
from src.processor import build_dataframe
from src.state_manager import update_snapshot
from src.token_store import get_access_token_from_store
from src.websocket_live import start_websocket


class MarketDataError(RuntimeError):
    pass


@dataclass
class MarketSnapshot:
    df: pd.DataFrame
    source: str
    spot: float | None = None
    message: str = ""
    is_live: bool = False


def get_market_snapshot() -> MarketSnapshot:
    errors: list[str] = []

    for source in _source_order():
        if source == "kite" and DATA_SOURCE == "auto" and not _kite_configured():
            errors.append("kite: missing KITE_API_KEY or KITE_ACCESS_TOKEN")
            continue

        try:
            if source == "kite":
                return _with_fallback_notes(_kite_snapshot(), errors)
            if source == "nse":
                return _with_fallback_notes(_nse_snapshot(), errors)
            if source == "bhavcopy":
                return _with_fallback_notes(_bhavcopy_snapshot(), errors)
            if source == "yfinance":
                return _with_fallback_notes(_yfinance_snapshot(), errors)
        except Exception as exc:
            errors.append(f"{source}: {exc}")

    raise MarketDataError("No market data source available. " + " | ".join(errors))


def _source_order() -> list[str]:
    if DATA_SOURCE in ("kite", "nse", "bhavcopy", "yfinance"):
        return [DATA_SOURCE]
    if DATA_SOURCE == "free":
        return ["nse", "bhavcopy", "yfinance"]
    return ["kite", "nse", "bhavcopy", "yfinance"]


def _with_fallback_notes(snapshot: MarketSnapshot, errors: list[str]) -> MarketSnapshot:
    if not errors:
        return snapshot

    notes = "Fallback notes: " + " | ".join(errors)
    snapshot.message = f"{snapshot.message} {notes}".strip()
    return snapshot


def _kite_configured() -> bool:
    return bool(KITE_API_KEY and get_access_token_from_store())


def _kite_snapshot() -> MarketSnapshot:
    tokens_df = get_weekly_nifty_tokens()
    token_map = {}

    for _, row in tokens_df.iterrows():
        token_map[int(row["instrument_token"])] = {
            "strike": row["strike"],
            "type": row["instrument_type"],
        }

    tokens = list(token_map.keys())
    live_ticks = start_websocket(tokens)
    time.sleep(2)
    delta = update_snapshot(live_ticks)

    if delta is None:
        return MarketSnapshot(
            df=pd.DataFrame(),
            source="Kite Connect live",
            message=f"Tracking {len(tokens)} instruments. Collecting initial snapshot...",
            is_live=True,
        )

    df = build_dataframe(delta, token_map)
    spot = float(df["strike"].median()) if not df.empty else None
    return MarketSnapshot(df=df, source="Kite Connect live", spot=spot, is_live=True)


def _nse_snapshot() -> MarketSnapshot:
    df, spot, source = fetch_nse_option_snapshot(UNDERLYING)
    message = "Using cached NSE data because the live NSE request failed." if "cached" in source else ""
    return MarketSnapshot(df=df, source=source, spot=spot, message=message)


def _bhavcopy_snapshot() -> MarketSnapshot:
    df, spot, source = fetch_bhavcopy_snapshot(UNDERLYING)
    return MarketSnapshot(
        df=df,
        source=source,
        spot=spot,
        message="Using delayed end-of-day bhavcopy because live free sources were unavailable.",
    )


def _yfinance_snapshot() -> MarketSnapshot:
    try:
        import yfinance as yf
    except ImportError as exc:
        raise MarketDataError("yfinance is not installed") from exc

    ticker = yf.Ticker(YFINANCE_SYMBOL)
    history = ticker.history(period="1d", interval="1m")
    if history.empty:
        raise MarketDataError(f"No yfinance candles returned for {YFINANCE_SYMBOL}")

    spot = float(history["Close"].dropna().iloc[-1])
    return MarketSnapshot(
        df=pd.DataFrame(),
        source=f"Yahoo Finance spot fallback ({YFINANCE_SYMBOL})",
        spot=spot,
        message="Yahoo Finance fallback only provides spot price, not option-chain OI rows.",
    )
