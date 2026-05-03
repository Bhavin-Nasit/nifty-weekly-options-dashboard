import os


class ConfigError(RuntimeError):
    pass


def _required(name: str) -> str:
    value = os.getenv(name)
    if value is None or str(value).strip() == "":
        raise ConfigError(f"Missing required environment variable: {name}")
    return str(value).strip()


def _as_int(name: str) -> int:
    value = _required(name)
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(f"Environment variable {name} must be an integer") from exc


def _as_float(name: str) -> float:
    value = _required(name)
    try:
        return float(value)
    except ValueError as exc:
        raise ConfigError(f"Environment variable {name} must be a number") from exc


def validate_required_config() -> dict:
    config = {
        "KITE_API_KEY": _required("KITE_API_KEY"),
        "KITE_API_SECRET": _required("KITE_API_SECRET"),
        "STRIKE_RANGE": _as_int("STRIKE_RANGE"),
        "OI_ALERT_THRESHOLD": _as_int("OI_ALERT_THRESHOLD"),
        "REFRESH_SECONDS": _as_int("REFRESH_SECONDS"),
        "DANGER_DISTANCE_POINTS": _as_int("DANGER_DISTANCE_POINTS"),
        "MIN_VOLUME_FOR_SIGNAL": _as_int("MIN_VOLUME_FOR_SIGNAL"),
        "ACCOUNT_CAPITAL": _as_float("ACCOUNT_CAPITAL"),
        "RISK_PER_TRADE_PCT": _as_float("RISK_PER_TRADE_PCT"),
        "MAX_LOTS": _as_int("MAX_LOTS"),
        "NIFTY_LOT_SIZE": _as_int("NIFTY_LOT_SIZE"),
        "OPTION_SL_MULTIPLIER": _as_float("OPTION_SL_MULTIPLIER"),
        "OPTION_TARGET_MULTIPLIER": _as_float("OPTION_TARGET_MULTIPLIER"),
        "SPREAD_WIDTH": _as_int("SPREAD_WIDTH"),
        "RANGE_DIFF_THRESHOLD": _as_int("RANGE_DIFF_THRESHOLD"),
        "MIN_SHORT_PREMIUM": _as_float("MIN_SHORT_PREMIUM"),
        "MAX_SHORT_PREMIUM": _as_float("MAX_SHORT_PREMIUM"),
    }

    if config["STRIKE_RANGE"] <= 0:
        raise ConfigError("STRIKE_RANGE must be greater than 0")
    if config["REFRESH_SECONDS"] <= 0:
        raise ConfigError("REFRESH_SECONDS must be greater than 0")
    if config["ACCOUNT_CAPITAL"] <= 0:
        raise ConfigError("ACCOUNT_CAPITAL must be greater than 0")
    if config["RISK_PER_TRADE_PCT"] <= 0:
        raise ConfigError("RISK_PER_TRADE_PCT must be greater than 0")
    if config["MAX_LOTS"] <= 0:
        raise ConfigError("MAX_LOTS must be greater than 0")
    if config["NIFTY_LOT_SIZE"] <= 0:
        raise ConfigError("NIFTY_LOT_SIZE must be greater than 0")
    if config["MIN_SHORT_PREMIUM"] <= 0:
        raise ConfigError("MIN_SHORT_PREMIUM must be greater than 0")
    if config["MAX_SHORT_PREMIUM"] <= config["MIN_SHORT_PREMIUM"]:
        raise ConfigError("MAX_SHORT_PREMIUM must be greater than MIN_SHORT_PREMIUM")

    return config
