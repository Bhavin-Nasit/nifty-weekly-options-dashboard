from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from src.config import NSE_MAX_RETRIES, NSE_TIMEOUT_SECONDS, STRIKE_RANGE


class NseDataError(RuntimeError):
    pass


_NSE_HOME = "https://www.nseindia.com/option-chain"
_NSE_API = "https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
_CACHE_FILE = Path("data/nse_option_chain_cache.json")
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
}


def fetch_nse_option_snapshot(symbol: str) -> tuple[pd.DataFrame, float | None, str]:
    payload, stale = _fetch_payload_with_cache(symbol)
    df, spot = _payload_to_dataframe(payload)
    source = "NSE option-chain snapshot"
    if stale:
        source += " (cached)"
    return df, spot, source


def _fetch_payload_with_cache(symbol: str) -> tuple[dict[str, Any], bool]:
    try:
        payload = _request_option_chain(symbol)
        _write_cache(payload)
        return payload, False
    except Exception as exc:
        cached = _read_cache()
        if cached:
            return cached, True
        raise NseDataError(f"NSE option-chain fetch failed and no cache is available: {exc}") from exc


def _request_option_chain(symbol: str) -> dict[str, Any]:
    retries = max(NSE_MAX_RETRIES, 1)
    url = _NSE_API.format(symbol=symbol.upper())
    last_error: Exception | None = None

    with requests.Session() as session:
        session.headers.update(_HEADERS)

        for attempt in range(retries):
            try:
                session.get(_NSE_HOME, timeout=NSE_TIMEOUT_SECONDS)
                response = session.get(url, timeout=NSE_TIMEOUT_SECONDS)

                if response.status_code in (401, 403):
                    session.cookies.clear()

                response.raise_for_status()
                return response.json()
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                if attempt < retries - 1:
                    time.sleep(min(2 * (attempt + 1), 5))

    raise NseDataError(f"NSE request failed after {retries} attempt(s): {last_error}")


def _payload_to_dataframe(payload: dict[str, Any]) -> tuple[pd.DataFrame, float | None]:
    records = payload.get("records") or {}
    rows = []
    spot = _as_float(records.get("underlyingValue"))
    expiry_dates = records.get("expiryDates") or []
    nearest_expiry = expiry_dates[0] if expiry_dates else None

    for item in records.get("data") or []:
        if nearest_expiry and item.get("expiryDate") != nearest_expiry:
            continue

        strike = _as_int(item.get("strikePrice"))
        if strike is None:
            continue

        for option_type in ("CE", "PE"):
            option = item.get(option_type)
            if not option:
                continue

            oi_change = _as_int(option.get("changeinOpenInterest")) or 0
            ltp_change = _as_float(option.get("change")) or 0.0
            rows.append(
                {
                    "strike": strike,
                    "type": option_type,
                    "expiry": item.get("expiryDate"),
                    "oi": _as_int(option.get("openInterest")) or 0,
                    "ltp": _as_float(option.get("lastPrice")) or 0.0,
                    "volume": _as_int(option.get("totalTradedVolume")) or 0,
                    "oi_change": oi_change,
                    "ltp_change": ltp_change,
                    "volume_change": _as_int(option.get("totalTradedVolume")) or 0,
                    "signal": _signal(option_type, oi_change, ltp_change),
                }
            )

    df = pd.DataFrame(rows)
    if df.empty:
        return df, spot

    df = _filter_atm_strikes(df, spot)
    return df.sort_values(["strike", "type"]).reset_index(drop=True), spot


def _filter_atm_strikes(df: pd.DataFrame, spot: float | None) -> pd.DataFrame:
    strikes = sorted(df["strike"].dropna().unique())
    if not strikes:
        return df

    center = spot if spot else float(df["strike"].median())
    nearest_index = min(range(len(strikes)), key=lambda idx: abs(strikes[idx] - center))
    start = max(nearest_index - STRIKE_RANGE, 0)
    end = min(nearest_index + STRIKE_RANGE + 1, len(strikes))
    allowed = set(strikes[start:end])
    return df[df["strike"].isin(allowed)]


def _signal(option_type: str, oi_change: int, ltp_change: float) -> str:
    if oi_change > 0 and ltp_change < 0:
        return f"{option_type} WRITING"
    if oi_change < 0 and ltp_change > 0:
        return f"{option_type} SHORT COVERING"
    if oi_change > 0 and ltp_change > 0:
        return f"{option_type} BUYING"
    if oi_change < 0 and ltp_change < 0:
        return f"{option_type} LONG UNWINDING"
    return "NEUTRAL"


def _write_cache(payload: dict[str, Any]) -> None:
    _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    wrapped = {"saved_at": int(time.time()), "payload": payload}
    _CACHE_FILE.write_text(json.dumps(wrapped), encoding="utf-8")


def _read_cache() -> dict[str, Any] | None:
    if not _CACHE_FILE.exists():
        return None

    try:
        wrapped = json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None

    payload = wrapped.get("payload")
    return payload if isinstance(payload, dict) else None


def _as_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
