from __future__ import annotations

import io
import zipfile
from datetime import date, timedelta
from typing import Any

import pandas as pd
import requests

from src.config import BHAVCOPY_LOOKBACK_DAYS, NSE_TIMEOUT_SECONDS, STRIKE_RANGE


class BhavcopyDataError(RuntimeError):
    pass


_BHAVCOPY_URL = "https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{date}_F_0000.csv.zip"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) "
        "Gecko/20100101 Firefox/124.0"
    ),
    "Accept": "application/zip,text/csv,*/*",
    "Connection": "keep-alive",
}


def fetch_bhavcopy_snapshot(symbol: str) -> tuple[pd.DataFrame, float | None, str]:
    errors: list[str] = []

    for report_date in _candidate_dates():
        try:
            raw = _download_bhavcopy(report_date)
            source_df = _read_zip_csv(raw)
            df, spot = _build_option_dataframe(source_df, symbol, report_date)
            if not df.empty:
                return df, spot, f"NSE FO bhavcopy EOD ({report_date:%Y-%m-%d})"

            errors.append(f"{report_date:%Y-%m-%d}: no {symbol} option rows")
        except Exception as exc:
            errors.append(f"{report_date:%Y-%m-%d}: {exc}")

    raise BhavcopyDataError("No NSE FO bhavcopy data available. " + " | ".join(errors[:5]))


def _candidate_dates() -> list[date]:
    today = date.today()
    days = []

    for offset in range(max(BHAVCOPY_LOOKBACK_DAYS, 1)):
        candidate = today - timedelta(days=offset)
        if candidate.weekday() < 5:
            days.append(candidate)

    return days


def _download_bhavcopy(report_date: date) -> bytes:
    url = _BHAVCOPY_URL.format(date=report_date.strftime("%Y%m%d"))
    response = requests.get(url, headers=_HEADERS, timeout=NSE_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.content


def _read_zip_csv(raw: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not csv_names:
            raise BhavcopyDataError("zip did not contain a CSV file")

        with archive.open(csv_names[0]) as csv_file:
            return pd.read_csv(csv_file)


def _build_option_dataframe(source_df: pd.DataFrame, symbol: str, report_date: date) -> tuple[pd.DataFrame, float | None]:
    normalized = source_df.rename(columns={column: column.strip() for column in source_df.columns})
    rows = []
    spot_values = []

    for _, row in normalized.iterrows():
        row_symbol = _text(_pick(row, "TckrSymb", "SYMBOL"))
        option_type = _text(_pick(row, "OptnTp", "OPTION_TYP"))

        if row_symbol != symbol.upper() or option_type not in ("CE", "PE"):
            continue

        expiry = _parse_date(_pick(row, "XpryDt", "EXPIRY_DT"))
        if expiry and expiry < report_date:
            continue

        strike = _as_int(_pick(row, "StrkPric", "STRIKE_PR"))
        if strike is None:
            continue

        open_price = _as_float(_pick(row, "OpnPric", "OPEN")) or 0.0
        close_price = _as_float(_pick(row, "ClsPric", "CLOSE", "LastPric")) or 0.0
        oi_change = _as_int(_pick(row, "ChngInOpnIntrst", "CHG_IN_OI")) or 0
        volume = _as_int(_pick(row, "TtlTradgVol", "CONTRACTS")) or 0
        spot = _as_float(_pick(row, "UndrlygPric", "UNDERLYING_VALUE"))
        if spot:
            spot_values.append(spot)

        rows.append(
            {
                "strike": strike,
                "type": option_type,
                "expiry": expiry.isoformat() if expiry else "",
                "oi": _as_int(_pick(row, "OpnIntrst", "OPEN_INT")) or 0,
                "ltp": close_price,
                "volume": volume,
                "oi_change": oi_change,
                "ltp_change": close_price - open_price,
                "volume_change": volume,
                "signal": _signal(option_type, oi_change, close_price - open_price),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df, None

    df = _nearest_expiry(df)
    spot = _median(spot_values) or float(df["strike"].median())
    df = _filter_atm_strikes(df, spot)
    return df.sort_values(["strike", "type"]).reset_index(drop=True), spot


def _nearest_expiry(df: pd.DataFrame) -> pd.DataFrame:
    expiries = sorted(expiry for expiry in df["expiry"].dropna().unique() if expiry)
    if not expiries:
        return df
    return df[df["expiry"] == expiries[0]]


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


def _pick(row: pd.Series, *names: str) -> Any:
    for name in names:
        if name in row:
            return row[name]
    return None


def _text(value: Any) -> str:
    if value in (None, "") or pd.isna(value):
        return ""
    return str(value).strip().upper()


def _parse_date(value: Any) -> date | None:
    if value in (None, "") or pd.isna(value):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def _as_int(value: Any) -> int | None:
    if value in (None, "") or pd.isna(value):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    if value in (None, "") or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(pd.Series(values).median())


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
