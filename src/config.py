import os
from dotenv import load_dotenv

load_dotenv()

KITE_API_KEY = os.getenv("KITE_API_KEY", "")
KITE_API_SECRET = os.getenv("KITE_API_SECRET", "")
KITE_ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

UNDERLYING = os.getenv("UNDERLYING", "NIFTY")
STRIKE_RANGE = int(os.getenv("STRIKE_RANGE", "10"))
OI_ALERT_THRESHOLD = int(os.getenv("OI_ALERT_THRESHOLD", "50000"))
REFRESH_SECONDS = int(os.getenv("REFRESH_SECONDS", "60"))
DANGER_DISTANCE_POINTS = int(os.getenv("DANGER_DISTANCE_POINTS", "100"))
MIN_VOLUME_FOR_SIGNAL = int(os.getenv("MIN_VOLUME_FOR_SIGNAL", "1000"))

# Risk controls
ACCOUNT_CAPITAL = float(os.getenv("ACCOUNT_CAPITAL", "200000"))
RISK_PER_TRADE_PCT = float(os.getenv("RISK_PER_TRADE_PCT", "1.0"))
MAX_LOTS = int(os.getenv("MAX_LOTS", "2"))
NIFTY_LOT_SIZE = int(os.getenv("NIFTY_LOT_SIZE", "75"))
OPTION_SL_MULTIPLIER = float(os.getenv("OPTION_SL_MULTIPLIER", "1.8"))
OPTION_TARGET_MULTIPLIER = float(os.getenv("OPTION_TARGET_MULTIPLIER", "0.5"))
SPREAD_WIDTH = int(os.getenv("SPREAD_WIDTH", "200"))
MIN_SHORT_PREMIUM = float(os.getenv("MIN_SHORT_PREMIUM", "20"))
MAX_SHORT_PREMIUM = float(os.getenv("MAX_SHORT_PREMIUM", "250"))

NIFTY_SPOT_SYMBOL = "NSE:NIFTY 50"
